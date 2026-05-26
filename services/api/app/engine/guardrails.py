"""
Guardrail validator — runs after the rules engine to surface problems
before the result is committed and shown to reviewers.
"""
from typing import Any

CONFIDENCE_ESCALATION_THRESHOLD = 0.55


def validate(
    case: Any,
    clauses: list[dict],
    decision: dict,
) -> dict:
    """
    Returns:
        {
            "status": "pass" | "warning" | "fail",
            "reasons": [str, ...]
        }
    """
    reasons: list[str] = []
    severity = "pass"

    def escalate(level: str, msg: str) -> None:
        nonlocal severity
        reasons.append(msg)
        if level == "fail" or (level == "warning" and severity == "pass"):
            severity = level

    # GR-1: No policy citations
    if not clauses:
        escalate("fail", "GR-1: No policy clauses were retrieved. Decision lacks evidentiary basis.")

    # GR-2: Conflicting hints in retrieved clauses
    hints = [c.get("determination_hint") for c in clauses if c.get("determination_hint")]
    unique_hints = set(h.lower() for h in hints if h)
    if "approve" in unique_hints and "deny" in unique_hints:
        escalate("fail", "GR-2: Retrieved clauses contain contradictory policy hints (approve vs deny).")

    # GR-3: Confidence below escalation threshold
    score = decision.get("confidence_score", 1.0)
    if score < CONFIDENCE_ESCALATION_THRESHOLD:
        escalate(
            "warning",
            f"GR-3: Confidence score {score:.2f} is below threshold {CONFIDENCE_ESCALATION_THRESHOLD}. "
            "Consider human review."
        )

    # GR-4: Missing clinical evidence for service requiring it
    clinical_required_codes = {"J0885", "J1745", "J1626", "Q2049"}
    if case.service_code in clinical_required_codes:
        notes = (case.clinical_notes_summary or "").strip()
        if not notes or len(notes) < 20:
            escalate(
                "fail",
                f"GR-4: Service {case.service_code} requires clinical documentation "
                "but none or insufficient notes were provided."
            )

    # GR-5: Rationale references no specific clause sections
    rationale = decision.get("rationale", "")
    has_section_ref = any(
        c["section"].lower() in rationale.lower() or c["clause_id"] in rationale
        for c in clauses
    )
    if clauses and not has_section_ref:
        escalate(
            "warning",
            "GR-5: Rationale does not explicitly reference any retrieved clause section."
        )

    return {"status": severity, "reasons": reasons}
