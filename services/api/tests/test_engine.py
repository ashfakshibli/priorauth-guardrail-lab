"""Unit tests for the deterministic engine components."""
import pytest
from unittest.mock import MagicMock
from app.engine.decision import run_rules_engine
from app.engine.guardrails import validate as guardrail_validate
from app.engine.evals import compute_evals


def _mock_case(service_code="J0885", diagnosis_codes=None, tags=None, clinical_notes="long enough notes here for validation"):
    case = MagicMock()
    case.id = "CASE-TEST"
    case.member_id = "MBR-0000"
    case.service_code = service_code
    case.diagnosis_codes = diagnosis_codes or []
    case.tags = tags or []
    case.clinical_notes_summary = clinical_notes
    return case


def _clause(hint, clause_id="CL-X", doc_id="DOC-1", section="S1", text="clause text", score=5):
    return {
        "clause_id": clause_id,
        "document_id": doc_id,
        "section": section,
        "clause_text": text,
        "tags": [],
        "determination_hint": hint,
        "relevance_score": score,
    }


# ── Decision engine ──────────────────────────────────────────────────────────

class TestDecisionEngine:
    def test_no_clauses_returns_human_review(self):
        case = _mock_case()
        result = run_rules_engine(case, [])
        assert result["determination"] == "human_review"
        assert result["confidence_score"] < 0.3

    def test_approve_hint_dominant(self):
        case = _mock_case()
        clauses = [_clause("approve"), _clause("approve")]
        result = run_rules_engine(case, clauses)
        assert result["determination"] == "approve"
        assert result["confidence_score"] > 0.5

    def test_deny_hint_dominant(self):
        case = _mock_case()
        clauses = [_clause("deny"), _clause("deny")]
        result = run_rules_engine(case, clauses)
        assert result["determination"] == "deny"
        assert result["confidence_score"] > 0.5

    def test_conflicting_hints_escalate(self):
        case = _mock_case()
        clauses = [_clause("approve"), _clause("deny")]
        result = run_rules_engine(case, clauses)
        assert result["determination"] == "human_review"

    def test_explicit_escalation_hint(self):
        case = _mock_case()
        clauses = [_clause("human_review")]
        result = run_rules_engine(case, clauses)
        assert result["determination"] == "human_review"

    def test_no_hints_defaults_to_approve(self):
        case = _mock_case()
        clauses = [_clause(None)]
        result = run_rules_engine(case, clauses)
        assert result["determination"] == "approve"

    def test_confidence_bounded(self):
        case = _mock_case()
        clauses = [_clause("approve")] * 10
        result = run_rules_engine(case, clauses)
        assert 0.0 <= result["confidence_score"] <= 1.0


# ── Guardrail validator ──────────────────────────────────────────────────────

class TestGuardrails:
    def test_no_clauses_fails(self):
        case = _mock_case()
        decision = {"determination": "approve", "confidence_score": 0.9, "rationale": "ok"}
        result = guardrail_validate(case, [], decision)
        assert result["status"] == "fail"
        assert any("GR-1" in r for r in result["reasons"])

    def test_contradictory_hints_fails(self):
        case = _mock_case()
        clauses = [_clause("approve"), _clause("deny")]
        decision = {"determination": "human_review", "confidence_score": 0.4, "rationale": "conflict"}
        result = guardrail_validate(case, clauses, decision)
        assert result["status"] == "fail"
        assert any("GR-2" in r for r in result["reasons"])

    def test_low_confidence_warns(self):
        case = _mock_case()
        clauses = [_clause("approve")]
        decision = {"determination": "approve", "confidence_score": 0.3, "rationale": "section S1 text"}
        result = guardrail_validate(case, clauses, decision)
        assert result["status"] in ("warning", "fail")
        assert any("GR-3" in r for r in result["reasons"])

    def test_missing_clinical_notes_fails_for_required_code(self):
        case = _mock_case(service_code="J0885", clinical_notes="")
        clauses = [_clause("approve", section="Section 3.1")]
        decision = {"determination": "approve", "confidence_score": 0.8, "rationale": "Section 3.1 covered"}
        result = guardrail_validate(case, clauses, decision)
        assert result["status"] == "fail"
        assert any("GR-4" in r for r in result["reasons"])

    def test_clean_decision_passes(self):
        case = _mock_case(service_code="72148")
        clauses = [_clause("approve", section="Section 2.1")]
        decision = {
            "determination": "approve",
            "confidence_score": 0.85,
            "rationale": "Section 2.1 conditions met",
        }
        result = guardrail_validate(case, clauses, decision)
        assert result["status"] == "pass"
        assert len(result["reasons"]) == 0


# ── Evals ────────────────────────────────────────────────────────────────────

class TestEvals:
    def test_missing_evidence_flagged(self):
        case = _mock_case()
        evals = compute_evals(case, [], {"determination": "human_review", "confidence_score": 0.1}, {"status": "fail"})
        assert evals["missing_evidence_flag"] is True
        assert evals["citation_presence"] is False

    def test_contradiction_flagged(self):
        case = _mock_case()
        clauses = [_clause("approve"), _clause("deny")]
        evals = compute_evals(case, clauses, {"determination": "human_review", "confidence_score": 0.4}, {"status": "fail"})
        assert evals["contradiction_flag"] is True

    def test_correct_escalation_is_scored(self):
        case = _mock_case()
        # human_review with low confidence → correct escalation
        evals = compute_evals(
            case, [_clause("approve")],
            {"determination": "human_review", "confidence_score": 0.3},
            {"status": "warning"},
        )
        assert evals["escalation_correctness"] is True

    def test_coverage_score_proportional(self):
        case = _mock_case()
        evals_one = compute_evals(case, [_clause("approve")], {"determination": "approve", "confidence_score": 0.9}, {"status": "pass"})
        evals_many = compute_evals(case, [_clause("approve")] * 4, {"determination": "approve", "confidence_score": 0.9}, {"status": "pass"})
        assert evals_many["policy_coverage_score"] >= evals_one["policy_coverage_score"]
