"""LLM proposes swaps; guardrails decide which ones survive."""
import json
import os

from .guardrails import Swap, curated_swaps, validate

SYSTEM = """You suggest ingredient substitutions for a home cook.
Rules: only use ingredients from the provided pantry list. Never suggest anything
unsafe, toxic, or that conflicts with the stated allergies. If no safe swap exists,
return an empty list. Do not invent ingredients. Respond with ONLY JSON:
{"swaps":[{"missing":"...","use":"...","note":"short reason"}]}"""


def suggest_swaps(recipe: str, missing: list[str], pantry: set[str],
                  allergies: set[str], tags: list[str]) -> list[Swap]:
    if not missing or "safety_critical" in tags:
        return []
    try:
        import anthropic
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model=os.getenv("PANTRY_MODEL", "claude-sonnet-5-5"),
            max_tokens=600, system=SYSTEM,
            messages=[{"role": "user", "content": json.dumps({
                "recipe": recipe, "missing": missing,
                "pantry": sorted(pantry), "allergies": sorted(allergies)})}])
        text = msg.content[0].text.strip().removeprefix("```json").removesuffix("```")
        proposed = [Swap(**s) for s in json.loads(text).get("swaps", [])]
    except Exception:
        proposed = curated_swaps(missing, pantry)   # offline / bad output fallback
    return validate(proposed, missing=missing, pantry=pantry, allergies=allergies, tags=tags)
