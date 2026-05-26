from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ── Policy ─────────────────────────────────────────────────────────────────

class PolicyClauseOut(BaseModel):
    id: str
    document_id: str
    section: str
    clause_text: str
    tags: list[str]
    determination_hint: Optional[str]

    class Config:
        from_attributes = True


class PolicyDocumentOut(BaseModel):
    id: str
    title: str
    payer_code: str
    effective_date: str
    description: Optional[str]
    clauses: list[PolicyClauseOut] = []

    class Config:
        from_attributes = True


# ── Cases ───────────────────────────────────────────────────────────────────

class CaseListItem(BaseModel):
    id: str
    member_id: str
    provider_id: str
    age_band: str
    service_code: str
    service_description: str
    status: str
    tags: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CaseDetail(BaseModel):
    id: str
    member_id: str
    provider_id: str
    age_band: str
    service_code: str
    service_description: str
    diagnosis_codes: list[str]
    clinical_notes_summary: Optional[str]
    policy_document_ids: list[str]
    status: str
    tags: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PolicyContextOut(BaseModel):
    case_id: str
    policy_documents: list[PolicyDocumentOut]


# ── Decision Run ─────────────────────────────────────────────────────────────

class DecisionRunOut(BaseModel):
    run_id: str
    case_id: str
    determination: str
    confidence_score: float
    policy_citations: list[dict]
    rationale_summary: str
    guardrail_status: str
    guardrail_reasons: list[str]
    latency_ms: int
    llm_enhanced: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Trace ────────────────────────────────────────────────────────────────────

class TraceEventOut(BaseModel):
    id: str
    step_name: str
    status: str
    started_at: datetime
    ended_at: datetime
    input_summary: str
    output_summary: str
    artifact_refs: list[str]
    warning_flags: list[str]
    sequence: int

    class Config:
        from_attributes = True


class TraceOut(BaseModel):
    run_id: str
    events: list[TraceEventOut]


# ── Evals ────────────────────────────────────────────────────────────────────

class EvalResultOut(BaseModel):
    run_id: str
    policy_coverage_score: float
    citation_presence: bool
    contradiction_flag: bool
    missing_evidence_flag: bool
    escalation_correctness: bool
    overall_eval_status: str

    class Config:
        from_attributes = True


# ── Review Queue ─────────────────────────────────────────────────────────────

class ReviewQueueItemOut(BaseModel):
    id: str
    run_id: str
    case_id: str
    reason: str
    priority: str
    assigned_to: Optional[str]
    resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True
