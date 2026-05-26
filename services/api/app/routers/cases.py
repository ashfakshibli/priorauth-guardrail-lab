from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Case, PolicyDocument
from app.schemas import CaseListItem, CaseDetail, PolicyContextOut, PolicyDocumentOut
from app.pipeline import run_decision_pipeline

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.get("", response_model=list[CaseListItem])
def list_cases(db: Session = Depends(get_db)):
    return db.query(Case).order_by(Case.created_at.desc()).all()


@router.get("/{case_id}", response_model=CaseDetail)
def get_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return case


@router.get("/{case_id}/policy-context", response_model=PolicyContextOut)
def get_policy_context(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    docs = (
        db.query(PolicyDocument)
        .filter(PolicyDocument.id.in_(case.policy_document_ids or []))
        .all()
    )
    return PolicyContextOut(case_id=case_id, policy_documents=docs)


@router.post("/{case_id}/run-decision")
def run_decision(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    try:
        result = run_decision_pipeline(case_id, db)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
