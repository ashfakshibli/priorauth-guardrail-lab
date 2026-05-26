# PriorAuth Guardrail Lab

A synthetic prior authorization decision engine built as a portfolio demo for healthcare workflow software. Demonstrates deterministic rules-based decision logic, guardrail validation, structured evaluation, and full execution tracing — without any real patient data.

> **DEMO DATA ONLY** — See [DEMO_DATA_ONLY.md](DEMO_DATA_ONLY.md). No PHI, no PII, no real payer integrations.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                              │
│         Next.js 15  (apps/web)  — TypeScript + Tailwind     │
└───────────────────────┬─────────────────────────────────────┘
                        │ REST / JSON
┌───────────────────────▼─────────────────────────────────────┐
│                  FastAPI  (services/api)                     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Decision Pipeline                      │   │
│  │  load_case → retrieve_clauses → rules_engine →     │   │
│  │  [optional LLM] → guardrail_validator →            │   │
│  │  eval_scoring → persist                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  SQLite (local)  /  Postgres (Heroku)                       │
└─────────────────────────────────────────────────────────────┘
```

### Key design decisions

| Decision | Rationale |
|---|---|
| Deterministic rules engine | LLM is optional — the system always produces a correct, traceable decision without an API key |
| LLM as rationale-only layer | Prevents LLM from being the authority on medical necessity; only rewrites the prose summary |
| Guardrail layer post-engine | Catches GR-1 (no citations), GR-2 (contradictions), GR-3 (low confidence), GR-4 (missing notes) |
| Structured evals | Policy coverage score, citation presence, contradiction flag, escalation correctness — all deterministic |
| Review queue auto-population | Cases with confidence < 0.55, guardrail fail, or human_review determination are queued automatically |

---

## Local Run

### Prerequisites
- Python 3.12+
- Node 20+
- (Optional) OpenAI-compatible API key for LLM rationale enhancement

### 1. API service

```bash
cd services/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # edit OPENAI_API_KEY if desired
uvicorn app.main:app --reload --port 8000
```

Swagger UI: http://localhost:8000/docs

### 2. Web app

```bash
cd apps/web
npm install
cp ../../.env.example .env.local   # or just set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Open http://localhost:3000

---

## Deploy to Heroku

### API

```bash
heroku create priorauth-api
heroku addons:create heroku-postgresql:essential-0 -a priorauth-api
heroku config:set OPENAI_API_KEY=<your-key> -a priorauth-api   # optional
git subtree push --prefix services/api heroku-api main
```

### Web

```bash
heroku create priorauth-web
heroku config:set NEXT_PUBLIC_API_URL=https://priorauth-api.herokuapp.com -a priorauth-web
git subtree push --prefix apps/web heroku-web main
```

---

## API Reference

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/api/cases` | List all seeded cases |
| GET | `/api/cases/{id}` | Case detail |
| GET | `/api/cases/{id}/policy-context` | Attached policy documents and clauses |
| POST | `/api/cases/{id}/run-decision` | Execute the full pipeline |
| GET | `/api/runs/{id}` | Decision run result |
| GET | `/api/runs/{id}/trace` | Step-by-step execution trace |
| GET | `/api/runs/{id}/evals` | Evaluation metrics |
| GET | `/api/review-queue` | Unresolved items requiring human review |

### `POST /api/cases/{id}/run-decision` — response shape

```json
{
  "run_id": "uuid",
  "determination": "approve | deny | human_review",
  "confidence_score": 0.87,
  "policy_citations": [
    { "clause_id": "CL-001-A", "document_id": "POL-MED-001",
      "section": "Section 3.1", "relevance_score": 11 }
  ],
  "rationale_summary": "...",
  "guardrail_status": "pass | warning | fail",
  "guardrail_reasons": [],
  "latency_ms": 42,
  "llm_enhanced": false
}
```

---

## Seeded Demo Cases

| Case | Service | Expected Determination | Pattern |
|---|---|---|---|
| CASE-1001 | J0885 Adalimumab | **approve** | Clearly covered — DMARD failure documented |
| CASE-1002 | 72148 MRI Lumbar | **deny** | Acute onset, no conservative treatment |
| CASE-1003 | H0018 Residential BH | **human_review** | IOP failure → escalation required |
| CASE-1004 | 29881 Knee Arthroscopy | **approve** | Confirmed tear, PT failed |
| CASE-1005 | J1745 Infliximab Infusion | **human_review** | Conflicting site-of-care signals |
| CASE-1006 | J0885 Adalimumab | **deny** | Missing clinical documentation |
| CASE-1007 | 78816 PET Scan | **approve** | Oncology-ordered, confirmed malignancy |
| CASE-1008 | 99999 Unlisted | **human_review** | No policy documents attached |

---

## Demo Script

1. Open http://localhost:3000
2. The **Cases** list shows 8 synthetic cases with status badges
3. Click **Review →** on CASE-1001 (Adalimumab, pending)
4. Read the case summary, diagnosis codes, and the full policy pack with clause hints
5. Click **Run Decision Engine** in the right panel
6. The **Decision** tab shows: determination=APPROVE, confidence bar, guardrail=PASS, rationale, and cited clauses
7. Switch to the **Trace** tab — expand each step to see input/output/timing
8. Switch to the **Evals** tab — review coverage score, citation presence, escalation correctness
9. Navigate back, open CASE-1002 (MRI acute onset) — observe DENY with GR-5 guardrail warning
10. Open CASE-1005 or CASE-1003 — observe HUMAN_REVIEW and watch the item appear in **Review Queue**

---

## Running Tests

```bash
# API
cd services/api && pytest -v

# Web (type check + lint)
cd apps/web && npm run typecheck && npm run lint
```

---

## Security & Hygiene

- CI runs `bandit`, `pip-audit`, `npm audit`, and `gitleaks` on every push
- No secrets committed — all configuration via environment variables
- LLM integration is opt-in and environment-driven (`OPENAI_API_KEY`)
- The system operates fully offline without any external API keys
- See [DEMO_DATA_ONLY.md](DEMO_DATA_ONLY.md) for the synthetic data statement
