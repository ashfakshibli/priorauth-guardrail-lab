"""
Synchronous decision pipeline.
Orchestrates: retrieve → decide → guardrail → eval → (optional LLM) → persist.
"""
from __future__ import annotations
import uuid
import time
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import (
    Case, DecisionRun, TraceEvent, EvalResult, ReviewQueueItem,
    DeterminationEnum, GuardrailStatusEnum, CaseStatusEnum
)
from app.engine.retrieval import retrieve_relevant_clauses
from app.engine.decision import run_rules_engine
from app.engine.guardrails import validate as guardrail_validate
from app.engine.evals import compute_evals
from app.engine import llm as llm_engine


def _trace_event(
    run_id: str,
    seq: int,
    step_name: str,
    status: str,
    started: datetime,
    ended: datetime,
    input_summary: str,
    output_summary: str,
    artifact_refs: list[str] | None = None,
    warning_flags: list[str] | None = None,
) -> TraceEvent:
    return TraceEvent(
        id=str(uuid.uuid4()),
        run_id=run_id,
        step_name=step_name,
        status=status,
        started_at=started,
        ended_at=ended,
        input_summary=input_summary,
        output_summary=output_summary,
        artifact_refs=artifact_refs or [],
        warning_flags=warning_flags or [],
        sequence=seq,
    )


def run_decision_pipeline(case_id: str, db: Session) -> dict:
    wall_start = time.time()
    case: Case | None = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise ValueError(f"Case {case_id} not found")

    run_id = str(uuid.uuid4())
    trace_events: list[TraceEvent] = []
    seq = 0

    # ── Step 1: Load case ───────────────────────────────────────────────────
    t0 = datetime.now(timezone.utc)
    t1 = datetime.now(timezone.utc)
    trace_events.append(_trace_event(
        run_id, seq := seq + 1, "load_case", "ok", t0, t1,
        f"case_id={case_id}",
        f"service={case.service_code}, member={case.member_id}, "
        f"policies={case.policy_document_ids}",
    ))

    # ── Step 2: Retrieve relevant clauses ───────────────────────────────────
    t0 = datetime.now(timezone.utc)
    try:
        clauses = retrieve_relevant_clauses(case, db)
        status = "ok"
        warns: list[str] = []
        if not clauses:
            warns.append("NO_CLAUSES_RETRIEVED")
    except Exception as exc:
        clauses = []
        status = "error"
        warns = [str(exc)]
    t1 = datetime.now(timezone.utc)
    trace_events.append(_trace_event(
        run_id, seq := seq + 1, "retrieve_clauses", status, t0, t1,
        f"doc_ids={case.policy_document_ids}, tags={case.tags}",
        f"{len(clauses)} clause(s) retrieved",
        artifact_refs=[c["clause_id"] for c in clauses],
        warning_flags=warns,
    ))

    # ── Step 3: Rules engine ─────────────────────────────────────────────────
    t0 = datetime.now(timezone.utc)
    decision = run_rules_engine(case, clauses)
    t1 = datetime.now(timezone.utc)
    trace_events.append(_trace_event(
        run_id, seq := seq + 1, "rules_engine", "ok", t0, t1,
        f"clauses_count={len(clauses)}",
        f"determination={decision['determination']}, "
        f"confidence={decision['confidence_score']}, "
        f"rule={decision['rule_triggered']}",
    ))

    # ── Step 4: Optional LLM rationale enhancement ───────────────────────────
    llm_used = False
    t0 = datetime.now(timezone.utc)
    if llm_engine.llm_available():
        try:
            case_summary = (
                f"Service: {case.service_description} ({case.service_code}). "
                f"Member: {case.member_id}, age-band: {case.age_band}. "
                f"Diagnoses: {', '.join(case.diagnosis_codes or [])}. "
                f"Notes: {(case.clinical_notes_summary or '')[:300]}"
            )
            enhanced = llm_engine.enhance_rationale(
                case_summary, clauses,
                decision["determination"],
                decision["rationale"],
            )
            decision["rationale"] = enhanced
            llm_used = True
            llm_status = "ok"
        except Exception as exc:
            llm_status = f"error: {exc}"
    else:
        llm_status = "skipped (no API key)"
    t1 = datetime.now(timezone.utc)
    trace_events.append(_trace_event(
        run_id, seq := seq + 1, "llm_enhancement", llm_status, t0, t1,
        f"llm_available={llm_engine.llm_available()}",
        f"enhanced={llm_used}",
    ))

    # ── Step 5: Guardrail validation ─────────────────────────────────────────
    t0 = datetime.now(timezone.utc)
    guardrail = guardrail_validate(case, clauses, decision)
    t1 = datetime.now(timezone.utc)
    trace_events.append(_trace_event(
        run_id, seq := seq + 1, "guardrail_validator", guardrail["status"], t0, t1,
        f"determination={decision['determination']}, confidence={decision['confidence_score']}",
        f"status={guardrail['status']}, reasons={guardrail['reasons']}",
        warning_flags=guardrail["reasons"],
    ))

    # ── Step 6: Eval scoring ─────────────────────────────────────────────────
    t0 = datetime.now(timezone.utc)
    evals = compute_evals(case, clauses, decision, guardrail)
    t1 = datetime.now(timezone.utc)
    trace_events.append(_trace_event(
        run_id, seq := seq + 1, "eval_scoring", "ok", t0, t1,
        "computed from prior steps",
        f"overall={evals['overall_eval_status']}, "
        f"coverage={evals['policy_coverage_score']}",
    ))

    # ── Step 7: Persist ───────────────────────────────────────────────────────
    latency_ms = int((time.time() - wall_start) * 1000)

    policy_citations = [
        {
            "clause_id": c["clause_id"],
            "document_id": c["document_id"],
            "section": c["section"],
            "relevance_score": c["relevance_score"],
        }
        for c in clauses
    ]

    determination_enum = DeterminationEnum(decision["determination"])
    guardrail_enum_map = {"pass": GuardrailStatusEnum.passed, "warning": GuardrailStatusEnum.warning, "fail": GuardrailStatusEnum.failed}
    guardrail_enum = guardrail_enum_map[guardrail["status"]]

    run = DecisionRun(
        id=run_id,
        case_id=case_id,
        determination=determination_enum,
        confidence_score=decision["confidence_score"],
        policy_citations=policy_citations,
        rationale_summary=decision["rationale"],
        guardrail_status=guardrail_enum,
        guardrail_reasons=guardrail["reasons"],
        latency_ms=latency_ms,
        llm_enhanced=llm_used,
    )
    db.add(run)

    for evt in trace_events:
        db.add(evt)

    eval_record = EvalResult(
        id=str(uuid.uuid4()),
        run_id=run_id,
        **evals,
    )
    db.add(eval_record)

    # Update case status
    status_map = {
        "approve": CaseStatusEnum.approved,
        "deny": CaseStatusEnum.denied,
        "human_review": CaseStatusEnum.under_review,
    }
    case.status = status_map[decision["determination"]]

    # Auto-queue for review when needed
    if (
        decision["determination"] == "human_review"
        or guardrail["status"] == "fail"
        or decision["confidence_score"] < 0.55
    ):
        priority = "high" if guardrail["status"] == "fail" else "medium"
        reason = "; ".join(guardrail["reasons"]) if guardrail["reasons"] else "Low confidence determination"
        queue_item = ReviewQueueItem(
            id=str(uuid.uuid4()),
            run_id=run_id,
            case_id=case_id,
            reason=reason,
            priority=priority,
        )
        db.add(queue_item)

    db.commit()

    return {
        "run_id": run_id,
        "case_id": case_id,
        "determination": decision["determination"],
        "confidence_score": decision["confidence_score"],
        "policy_citations": policy_citations,
        "rationale_summary": decision["rationale"],
        "guardrail_status": guardrail["status"],
        "guardrail_reasons": guardrail["reasons"],
        "latency_ms": latency_ms,
        "llm_enhanced": llm_used,
        "created_at": run.created_at,
    }
