"""
Deterministic rules engine.  The LLM layer may later enhance the rationale
but NEVER overrides the determination produced here.
"""
from typing import Any


CONFLICT_MARGIN = 0.15  # escalate only when winning side leads by less than 15% of max weight


def _hint_weights(clauses: list[dict]) -> dict[str, float]:
    """Sum relevance scores per hint type for weighted conflict resolution."""
    weights: dict[str, float] = {"approve": 0.0, "deny": 0.0, "human_review": 0.0}
    for c in clauses:
        hint = (c.get("determination_hint") or "").lower()
        if hint in weights:
            weights[hint] += c.get("relevance_score", 1)
    return weights


def _hint_votes(clauses: list[dict]) -> dict[str, int]:
    votes: dict[str, int] = {"approve": 0, "deny": 0, "human_review": 0}
    for c in clauses:
        hint = (c.get("determination_hint") or "").lower()
        if hint in votes:
            votes[hint] += 1
    return votes


def _base_confidence(clauses: list[dict], weights: dict[str, float]) -> float:
    if not clauses:
        return 0.0
    top_weight = max(weights.values(), default=0.0)
    total_weight = sum(weights.values())
    if total_weight == 0:
        return 0.4
    confidence = min(0.95, 0.5 + (top_weight / max(total_weight, 1)) * 0.45)
    return round(confidence, 3)


def run_rules_engine(case: Any, clauses: list[dict]) -> dict:
    """
    Apply deterministic rules to produce a determination.

    Rules (in priority order):
    1. No relevant clauses → human_review (missing evidence)
    2. Conflicting deny + approve hints → resolve by weighted relevance score.
       Only escalate when scores are within CONFLICT_MARGIN of each other.
    3. Explicit deny dominates (no approve hints)
    4. Explicit approve dominates (no deny hints)
    5. Explicit escalation hint only
    6. No hints, clauses exist → approve with moderate confidence
    """
    votes = _hint_votes(clauses)
    weights = _hint_weights(clauses)
    confidence = _base_confidence(clauses, weights)

    # Rule 1: no clauses retrieved
    if not clauses:
        return {
            "determination": "human_review",
            "confidence_score": 0.1,
            "rule_triggered": "NO_RELEVANT_CLAUSES",
            "rationale": (
                f"No policy clauses matched case {case.id} "
                f"(service {case.service_code}). Manual review required."
            ),
        }

    deny_count = votes["deny"]
    approve_count = votes["approve"]
    review_count = votes["human_review"]
    approve_weight = weights["approve"]
    deny_weight = weights["deny"]

    # Rule 2: conflict — resolve by weighted relevance score
    if deny_count > 0 and approve_count > 0:
        max_weight = max(approve_weight, deny_weight)
        if max_weight == 0:
            margin = 0.0
        else:
            margin = abs(approve_weight - deny_weight) / max_weight

        if margin < CONFLICT_MARGIN:
            # Scores too close to call — escalate
            return {
                "determination": "human_review",
                "confidence_score": round(confidence * 0.55, 3),
                "rule_triggered": "CONFLICTING_POLICY_HINTS_TIED",
                "rationale": (
                    f"Approve-weighted score ({approve_weight:.0f}) and deny-weighted score "
                    f"({deny_weight:.0f}) are within conflict margin. Escalating for review."
                ),
            }
        elif deny_weight > approve_weight:
            return {
                "determination": "deny",
                "confidence_score": round(confidence * 0.8, 3),
                "rule_triggered": "DENY_WEIGHTED_DOMINANT",
                "rationale": (
                    f"Service {case.service_code} for member {case.member_id} — "
                    f"denial clauses outweigh coverage clauses by relevance "
                    f"(deny={deny_weight:.0f}, approve={approve_weight:.0f})."
                ),
            }
        else:
            return {
                "determination": "approve",
                "confidence_score": round(confidence * 0.8, 3),
                "rule_triggered": "APPROVE_WEIGHTED_DOMINANT",
                "rationale": (
                    f"Service {case.service_code} for member {case.member_id} — "
                    f"coverage clauses outweigh denial clauses by relevance "
                    f"(approve={approve_weight:.0f}, deny={deny_weight:.0f})."
                ),
            }

    # Rule 3: explicit deny dominates (no approve hints)
    if deny_count > 0:
        return {
            "determination": "deny",
            "confidence_score": confidence,
            "rule_triggered": "DENY_HINT_DOMINANT",
            "rationale": (
                f"Service {case.service_code} for member {case.member_id} "
                f"matched {deny_count} denial clause(s) with no offsetting coverage."
            ),
        }

    # Rule 4: approve vs human_review coexistence — weight decides
    if approve_count > 0 and review_count > 0:
        if weights["human_review"] >= weights["approve"]:
            return {
                "determination": "human_review",
                "confidence_score": round(confidence * 0.65, 3),
                "rule_triggered": "REVIEW_OUTWEIGHS_APPROVE",
                "rationale": (
                    f"Service {case.service_code} has coverage-indicating clauses, "
                    "but escalation-requiring clauses carry equal or greater relevance. "
                    "Routing to human review."
                ),
            }
        return {
            "determination": "approve",
            "confidence_score": round(confidence * 0.8, 3),
            "rule_triggered": "APPROVE_DOMINANT_OVER_REVIEW",
            "rationale": (
                f"Service {case.service_code} for member {case.member_id} — "
                "coverage clauses outweigh escalation clauses by relevance. Approving."
            ),
        }

    # Rule 5: explicit approve with no escalation signals
    if approve_count > 0:
        return {
            "determination": "approve",
            "confidence_score": confidence,
            "rule_triggered": "APPROVE_HINT_DOMINANT",
            "rationale": (
                f"Service {case.service_code} for member {case.member_id} "
                f"matched {approve_count} coverage clause(s) with no denial indicators."
            ),
        }

    # Rule 6: explicit escalation hint only
    if review_count > 0:
        return {
            "determination": "human_review",
            "confidence_score": round(confidence * 0.7, 3),
            "rule_triggered": "ESCALATION_HINT",
            "rationale": (
                f"{review_count} clause(s) explicitly require human review "
                f"for service {case.service_code}."
            ),
        }

    # Rule 6: clauses found but no hints → default approve with lower confidence
    return {
        "determination": "approve",
        "confidence_score": round(confidence * 0.7, 3),
        "rule_triggered": "DEFAULT_APPROVE_NO_HINTS",
        "rationale": (
            f"Relevant clauses found for service {case.service_code} but none "
            "provided an explicit determination hint. Defaulting to approve "
            "with reduced confidence."
        ),
    }
