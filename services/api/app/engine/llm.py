"""
Optional LLM enhancement layer.
Called AFTER the deterministic engine has produced a final determination.
The LLM may only rewrite the rationale summary and add reviewer notes.
It NEVER changes the determination, confidence, or citations.
"""
import os
import logging

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return None
    try:
        from openai import OpenAI
        _client = OpenAI(
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        )
        return _client
    except Exception as exc:
        logger.warning("LLM client init failed: %s", exc)
        return None


def enhance_rationale(
    case_summary: str,
    clauses: list[dict],
    determination: str,
    base_rationale: str,
) -> str:
    """
    Returns an enhanced rationale string.
    Falls back to base_rationale if LLM is unavailable.
    """
    client = _get_client()
    if client is None:
        return base_rationale

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    clauses_text = "\n".join(
        f"- [{c['clause_id']}] {c['section']}: {c['clause_text'][:200]}"
        for c in clauses[:4]
    )
    prompt = (
        "You are a prior authorization specialist reviewing a synthetic demo case. "
        "Your job is to write a concise, professional rationale for the determination below. "
        "Do not change the determination. Cite the clause IDs in your explanation.\n\n"
        f"Case summary:\n{case_summary}\n\n"
        f"Determination: {determination.upper()}\n\n"
        f"Supporting clauses:\n{clauses_text}\n\n"
        f"Base rationale: {base_rationale}\n\n"
        "Write the enhanced rationale in 2-3 sentences:"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.2,
        )
        text = response.choices[0].message.content or base_rationale
        return text.strip()
    except Exception as exc:
        logger.warning("LLM enhance_rationale failed: %s — using base rationale", exc)
        return base_rationale


def llm_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY", ""))
