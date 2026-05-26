"""
Deterministic clause retrieval via tag intersection and keyword scoring.
No embeddings or LLM required.
"""
from typing import Any
from sqlalchemy.orm import Session
from app.models import PolicyClause, PolicyDocument


MIN_RELEVANCE_SCORE = 6  # requires at least two tag overlaps before a clause influences the decision


def retrieve_relevant_clauses(
    case: Any, db: Session, top_k: int = 6
) -> list[dict]:
    """
    Score every clause in attached policy documents against the case.
    Returns top-k clauses sorted by relevance score descending.
    """
    doc_ids: list[str] = case.policy_document_ids or []
    if not doc_ids:
        return []

    clauses = (
        db.query(PolicyClause)
        .join(PolicyDocument)
        .filter(PolicyDocument.id.in_(doc_ids))
        .all()
    )

    case_tags = set(case.tags or [])
    diag_codes = set(case.diagnosis_codes or [])
    service_code = (case.service_code or "").upper()

    scored: list[tuple[int, PolicyClause]] = []
    for clause in clauses:
        score = 0
        clause_tags = set(clause.tags or [])

        # Tag overlap is the primary signal
        overlap = case_tags & clause_tags
        score += len(overlap) * 3

        # Diagnosis code mentioned in clause text (weaker signal than tag overlap)
        for dx in diag_codes:
            if dx.upper() in (clause.clause_text or "").upper():
                score += 2

        # Clause has a determination hint (strong signal)
        if clause.determination_hint:
            score += 2

        scored.append((score, clause))

    scored.sort(key=lambda t: t[0], reverse=True)
    # Filter out low-signal clauses before taking top_k
    scored = [(s, c) for s, c in scored if s >= MIN_RELEVANCE_SCORE]
    top = scored[:top_k]

    return [
        {
            "clause_id": c.id,
            "document_id": c.document_id,
            "section": c.section,
            "clause_text": c.clause_text,
            "tags": c.tags or [],
            "determination_hint": c.determination_hint,
            "relevance_score": s,
        }
        for s, c in top
    ]
