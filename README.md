# PriorAuth Guardrail Lab

A synthetic prior authorization decision engine built as a portfolio demo for healthcare workflow software. Demonstrates deterministic rules-based decision logic, guardrail validation, structured evaluation, and full execution tracing — without any real patient data.

> **DEMO DATA ONLY** — See [DEMO_DATA_ONLY.md](DEMO_DATA_ONLY.md). No PHI, no PII, no real payer integrations.

## Live Demo

| | URL |
|---|---|
| **Web App** | https://priorauth-web-6dbd68214f7f.herokuapp.com |
| **API** | https://priorauth-api-a1bc3b3b3d0c.herokuapp.com |
| **API Docs (Swagger)** | https://priorauth-api-a1bc3b3b3d0c.herokuapp.com/docs |

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

Pushes to `main` auto-deploy via GitHub Actions: tests run first, then each subdirectory is packaged and force-pushed to its Heroku remote.

| App | Heroku remote | Trigger path |
|---|---|---|
| API (FastAPI + Python 3.12) | `priorauth-api` | `services/api/**` |
| Web (Next.js) | `priorauth-web` | `apps/web/**` |

### Manual first-time setup

```bash
heroku create priorauth-api && heroku create priorauth-web
heroku addons:create heroku-postgresql:essential-0 -a priorauth-api
heroku config:set NEXT_PUBLIC_API_URL=https://<api-app>.herokuapp.com \
  NPM_CONFIG_PRODUCTION=false -a priorauth-web
heroku config:set OPENAI_API_KEY=<your-key> -a priorauth-api   # optional

# Secrets required in GitHub repo:
# HEROKU_API_KEY  — from `heroku auth:token`
# HEROKU_EMAIL    — your Heroku account email
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

## Policy Data Sources

Policy clause text is adapted from **public-domain CMS coverage documents** — no license restrictions, no PHI. This gives the guardrail and eval logic something realistic to cite rather than purely invented criteria.

| Policy Doc | CMS Source | Key Criteria Captured |
|---|---|---|
| **POL-MED-001** – Biologics | [CMS Article A52423](https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleId=52423) | MTX + 1 DMARD failure × 90 days; ACR 20% TJC/SJC improvement threshold; step-therapy exception pathway |
| **POL-IMG-002** – MRI | [NCD 220.2](https://www.cms.gov/medicare-coverage-database/view/ncd.aspx?NCDId=282) + [LCD L34220](https://www.cms.gov/medicare-coverage-database/) | 6-week conservative-care gate; red-flag bypass list (neuro deficit, malignancy, infection, trauma) |
| **POL-IMG-002** – PET | [NCD 220.6.17](https://www.cms.gov/medicare-coverage-database/view/ncd.aspx?NCDId=229) | Initial anti-tumor strategy; histologic confirmation required; ≤ 3 treatment-response scans |
| **POL-BH-003** – Behavioral Health | [LCD L33626](https://www.cms.gov/medicare-coverage-database/view/lcd.aspx?LCDId=33626) (Novitas) | PHP criteria; 8-week / 9 hr/week IOP failure before residential; concurrent review required |
| **POL-SURG-004** – Knee Surgery | [NCD 150.9](https://www.cms.gov/medicare-coverage-database/view/ncd.aspx?NCDId=199) guidance | Mechanical symptoms (locking/catching/giving way) required; degenerative OA pain-only excluded |
| **POL-PHARM-005** – Infusion | [CMS Article A52423](https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleId=52423) | 2 uneventful infusion-center doses before home transition; prior reactions → mandatory infusion-center |

### Before / After: Clause Quality Comparison

The swap from fully synthetic text to CMS-derived language sharpens the decision engine — the rules engine now matches on clinical thresholds that mirror real payer criteria rather than invented ones.

**Before (synthetic):**
```
"MRI of the lumbar spine (CPT 72148) is covered when the member has
 low back pain lasting > 6 weeks with documented conservative treatment
 failure, OR red-flag symptoms (e.g., neurological deficits, cancer history)."
```

**After (CMS NCD 220.2 / LCD L34220 adapted):**
```
"MRI of the lumbar spine (CPT 72148) is covered when the member has
 low back pain with a duration exceeding six (6) weeks AND documented
 failure of conservative treatment, defined as physician-directed physical
 therapy, activity modification, or analgesic therapy. Coverage is also
 approved without the six-week waiting period when red-flag indicators
 are present, including: new neurological deficit (radiculopathy, bowel
 or bladder dysfunction), history of malignancy with suspected metastatic
 disease, fever with suspected spinal infection, or acute trauma.
 Per CMS NCD 220.2, MRI is a covered service when clinically indicated
 and ordered by the treating physician."
```

The revised clause surfaces the specific NCD number, enumerates all four red-flag categories, and uses regulatory phrasing — giving the LLM rationale layer and the eval scoring model grounded language to work with.

> All clause text is adapted for demo purposes. Source documents are U.S. government works in the public domain. See [DEMO_DATA_ONLY.md](DEMO_DATA_ONLY.md).

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
