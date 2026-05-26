"""API integration tests using TestClient against seeded data."""
import pytest


class TestHealth:
    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestCasesList:
    def test_returns_seeded_cases(self, client):
        r = client.get("/api/cases")
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 8
        ids = [c["id"] for c in data]
        assert "CASE-1001" in ids

    def test_case_items_have_required_fields(self, client):
        r = client.get("/api/cases")
        item = r.json()[0]
        for field in ["id", "member_id", "provider_id", "service_code", "status", "created_at"]:
            assert field in item


class TestCaseDetail:
    def test_existing_case(self, client):
        r = client.get("/api/cases/CASE-1001")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == "CASE-1001"
        assert data["service_code"] == "J0885"

    def test_missing_case_404(self, client):
        r = client.get("/api/cases/CASE-9999")
        assert r.status_code == 404

    def test_policy_context(self, client):
        r = client.get("/api/cases/CASE-1001/policy-context")
        assert r.status_code == 200
        data = r.json()
        assert "policy_documents" in data
        assert len(data["policy_documents"]) >= 1
        assert data["case_id"] == "CASE-1001"


class TestRunDecision:
    def test_run_decision_returns_valid_structure(self, client):
        r = client.post("/api/cases/CASE-1004/run-decision")
        assert r.status_code == 200
        data = r.json()
        assert "run_id" in data
        assert data["determination"] in ("approve", "deny", "human_review")
        assert 0.0 <= data["confidence_score"] <= 1.0
        assert data["guardrail_status"] in ("pass", "warning", "fail")
        assert isinstance(data["policy_citations"], list)
        assert isinstance(data["guardrail_reasons"], list)
        assert data["latency_ms"] >= 0

    def test_clearly_approvable_case(self, client):
        # CASE-1001: biologic with documented DMARD failure → approve
        r = client.post("/api/cases/CASE-1001/run-decision")
        data = r.json()
        assert data["determination"] == "approve"

    def test_clearly_deniable_case(self, client):
        # CASE-1002: acute MRI < 6 weeks, no red flags → deny
        r = client.post("/api/cases/CASE-1002/run-decision")
        data = r.json()
        assert data["determination"] == "deny"

    def test_missing_evidence_case(self, client):
        # CASE-1008: no policy docs attached → human_review
        r = client.post("/api/cases/CASE-1008/run-decision")
        data = r.json()
        assert data["determination"] == "human_review"

    def test_run_persists_trace(self, client):
        r = client.post("/api/cases/CASE-1007/run-decision")
        run_id = r.json()["run_id"]
        tr = client.get(f"/api/runs/{run_id}/trace")
        assert tr.status_code == 200
        events = tr.json()["events"]
        assert len(events) >= 4
        step_names = [e["step_name"] for e in events]
        assert "rules_engine" in step_names
        assert "guardrail_validator" in step_names

    def test_run_persists_evals(self, client):
        r = client.post("/api/cases/CASE-1004/run-decision")
        run_id = r.json()["run_id"]
        ev = client.get(f"/api/runs/{run_id}/evals")
        assert ev.status_code == 200
        data = ev.json()
        assert "policy_coverage_score" in data
        assert "overall_eval_status" in data

    def test_invalid_case_404(self, client):
        r = client.post("/api/cases/CASE-FAKE/run-decision")
        assert r.status_code == 404

    def test_llm_disabled_still_works(self, client, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        r = client.post("/api/cases/CASE-1004/run-decision")
        assert r.status_code == 200
        assert r.json()["llm_enhanced"] is False


class TestRunEndpoints:
    def test_get_run(self, client):
        r = client.post("/api/cases/CASE-1007/run-decision")
        run_id = r.json()["run_id"]
        r2 = client.get(f"/api/runs/{run_id}")
        assert r2.status_code == 200
        assert r2.json()["run_id"] == run_id

    def test_missing_run_404(self, client):
        r = client.get("/api/runs/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404


class TestReviewQueue:
    def test_review_queue_returns_list(self, client):
        # First generate some human_review decisions
        client.post("/api/cases/CASE-1003/run-decision")
        r = client.get("/api/review-queue")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_queue_items_have_required_fields(self, client):
        client.post("/api/cases/CASE-1005/run-decision")
        r = client.get("/api/review-queue")
        items = r.json()
        if items:
            item = items[0]
            for field in ["id", "run_id", "case_id", "reason", "priority", "resolved"]:
                assert field in item
