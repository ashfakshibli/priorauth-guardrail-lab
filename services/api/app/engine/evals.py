"""
Deterministic eval scoring.  Produces structured metrics for the Trace/Evals tab.
All logic is rule-based — no LLM involvement.
"""
from typing import Any


COVERAGE_CLAUSE_MINIMUM = 2
HIGH_CONFIDENCE_THRESHOLD = 0.75


def compute_evals(
    case: Any,
    clauses: list[dict],
    decision: dict,
    guardrail: dict,
) -> dict:
    determination = decision.get("determination", "")
    confidence = decision.get("confidence_score", 0.0)
    hints = [c.get("determination_hint", "").lower() for c in clauses if c.get("determination_hint")]
    unique_hints = set(hints)

    # Metric 1: policy_coverage_score (0-1)
    n = len(clauses)
    coverage_score = min(1.0, n / max(COVERAGE_CLAUSE_MINIMUM, 1))
    coverage_score = round(coverage_score, 3)

    # Metric 2: citation_presence — at least one clause retrieved
    citation_presence = len(clauses) > 0

    # Metric 3: contradiction_flag
    contradiction_flag = "approve" in unique_hints and "deny" in unique_hints

    # Metric 4: missing_evidence_flag
    missing_evidence_flag = len(clauses) == 0

    # Metric 5: escalation_correctness
    # A human_review determination is "correct" when:
    #   - confidence < HIGH_CONFIDENCE_THRESHOLD, OR
    #   - contradictions detected, OR
    #   - guardrail failed
    needs_escalation = (
        confidence < HIGH_CONFIDENCE_THRESHOLD
        or contradiction_flag
        or guardrail.get("status") == "fail"
    )
    if determination == "human_review":
        escalation_correctness = needs_escalation
    else:
        escalation_correctness = not needs_escalation

    # Overall status
    if missing_evidence_flag or contradiction_flag or not escalation_correctness:
        overall_eval_status = "fail"
    elif coverage_score < 0.5 or not citation_presence:
        overall_eval_status = "warning"
    else:
        overall_eval_status = "pass"

    return {
        "policy_coverage_score": coverage_score,
        "citation_presence": citation_presence,
        "contradiction_flag": contradiction_flag,
        "missing_evidence_flag": missing_evidence_flag,
        "escalation_correctness": escalation_correctness,
        "overall_eval_status": overall_eval_status,
    }
