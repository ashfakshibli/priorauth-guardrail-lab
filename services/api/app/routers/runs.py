from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DecisionRun, TraceEvent, EvalResult
from app.schemas import DecisionRunOut, TraceOut, TraceEventOut, EvalResultOut

router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.get("/{run_id}", response_model=DecisionRunOut)
def get_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(DecisionRun).filter(DecisionRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return DecisionRunOut(
        run_id=run.id,
        case_id=run.case_id,
        determination=run.determination.value,
        confidence_score=run.confidence_score,
        policy_citations=run.policy_citations or [],
        rationale_summary=run.rationale_summary or "",
        guardrail_status=run.guardrail_status.value,
        guardrail_reasons=run.guardrail_reasons or [],
        latency_ms=run.latency_ms or 0,
        llm_enhanced=run.llm_enhanced,
        created_at=run.created_at,
    )


@router.get("/{run_id}/trace", response_model=TraceOut)
def get_trace(run_id: str, db: Session = Depends(get_db)):
    run = db.query(DecisionRun).filter(DecisionRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    events = (
        db.query(TraceEvent)
        .filter(TraceEvent.run_id == run_id)
        .order_by(TraceEvent.sequence)
        .all()
    )
    return TraceOut(run_id=run_id, events=events)


@router.get("/{run_id}/evals", response_model=EvalResultOut)
def get_evals(run_id: str, db: Session = Depends(get_db)):
    run = db.query(DecisionRun).filter(DecisionRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    eval_rec = db.query(EvalResult).filter(EvalResult.run_id == run_id).first()
    if not eval_rec:
        raise HTTPException(status_code=404, detail="Eval results not found for this run")
    return EvalResultOut(run_id=run_id, **{
        k: getattr(eval_rec, k)
        for k in [
            "policy_coverage_score", "citation_presence", "contradiction_flag",
            "missing_evidence_flag", "escalation_correctness", "overall_eval_status",
        ]
    })
