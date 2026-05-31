from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime,
    ForeignKey, JSON, Enum as SAEnum
)
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class DeterminationEnum(str, enum.Enum):
    approve = "approve"
    deny = "deny"
    human_review = "human_review"


class GuardrailStatusEnum(str, enum.Enum):
    passed = "pass"
    warning = "warning"
    failed = "fail"


class CaseStatusEnum(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    denied = "denied"
    under_review = "under_review"


class PolicyDocument(Base):
    __tablename__ = "policy_documents"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    payer_code = Column(String, nullable=False)
    effective_date = Column(String, nullable=False)
    description = Column(Text)
    clauses = relationship("PolicyClause", back_populates="document", cascade="all, delete-orphan")


class PolicyClause(Base):
    __tablename__ = "policy_clauses"

    id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey("policy_documents.id"), nullable=False)
    section = Column(String, nullable=False)
    clause_text = Column(Text, nullable=False)
    tags = Column(JSON, default=list)
    determination_hint = Column(String)
    document = relationship("PolicyDocument", back_populates="clauses")


class Case(Base):
    __tablename__ = "cases"

    id = Column(String, primary_key=True)
    member_id = Column(String, nullable=False)
    provider_id = Column(String, nullable=False)
    age_band = Column(String, nullable=False)
    service_code = Column(String, nullable=False)
    service_description = Column(String, nullable=False)
    diagnosis_codes = Column(JSON, default=list)
    clinical_notes_summary = Column(Text)
    policy_document_ids = Column(JSON, default=list)
    status = Column(SAEnum(CaseStatusEnum), default=CaseStatusEnum.pending)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    tags = Column(JSON, default=list)
    runs = relationship("DecisionRun", back_populates="case", cascade="all, delete-orphan")


class DecisionRun(Base):
    __tablename__ = "decision_runs"

    id = Column(String, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    determination = Column(SAEnum(DeterminationEnum), nullable=False)
    confidence_score = Column(Float, nullable=False)
    policy_citations = Column(JSON, default=list)
    rationale_summary = Column(Text)
    guardrail_status = Column(SAEnum(GuardrailStatusEnum), nullable=False)
    guardrail_reasons = Column(JSON, default=list)
    latency_ms = Column(Integer)
    llm_enhanced = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    case = relationship("Case", back_populates="runs")
    trace_events = relationship("TraceEvent", back_populates="run", cascade="all, delete-orphan")
    eval_results = relationship("EvalResult", back_populates="run", cascade="all, delete-orphan", uselist=False)
    review_queue_item = relationship("ReviewQueueItem", back_populates="run", cascade="all, delete-orphan", uselist=False)


class TraceEvent(Base):
    __tablename__ = "trace_events"

    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("decision_runs.id"), nullable=False)
    step_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=False)
    input_summary = Column(Text)
    output_summary = Column(Text)
    artifact_refs = Column(JSON, default=list)
    warning_flags = Column(JSON, default=list)
    sequence = Column(Integer, nullable=False)
    run = relationship("DecisionRun", back_populates="trace_events")


class EvalResult(Base):
    __tablename__ = "eval_results"

    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("decision_runs.id"), nullable=False, unique=True)
    policy_coverage_score = Column(Float, nullable=False)
    citation_presence = Column(Boolean, nullable=False)
    contradiction_flag = Column(Boolean, nullable=False)
    missing_evidence_flag = Column(Boolean, nullable=False)
    escalation_correctness = Column(Boolean, nullable=False)
    overall_eval_status = Column(String, nullable=False)
    run = relationship("DecisionRun", back_populates="eval_results")


class ReviewQueueItem(Base):
    __tablename__ = "review_queue_items"

    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("decision_runs.id"), nullable=False, unique=True)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    reason = Column(Text, nullable=False)
    priority = Column(String, nullable=False)
    assigned_to = Column(String)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    run = relationship("DecisionRun", back_populates="review_queue_item")
