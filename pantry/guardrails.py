"""Safety layer: every LLM-proposed swap must pass these checks or it is dropped."""
from dataclasses import dataclass

from .matcher import normalize

ALLERGENS = {
    "dairy": {"milk", "butter", "cheese", "cream", "yogurt", "greek yogurt", "sour cream", "buttermilk"},
    "egg": {"egg", "mayonnaise"},
    "gluten": {"flour", "pasta", "bread", "soy sauce", "couscous"},
    "nuts": {"almond", "walnut", "cashew", "peanut", "almond milk", "pecan"},
    "soy": {"soy sauce", "soy milk", "tofu"},
}
TOXIC_OR_RISKY = {"raw kidney bean", "bitter almond", "apricot kernel", "raw cassava",
                  "raw elderberry", "wild mushroom", "bleach", "raw egg"}
# Curated fallback table: safe, commonly accepted swaps.
CURATED = {"butter": ["olive oil"], "milk": ["oat milk", "soy milk"], "honey": ["maple syrup"],
           "green onion": ["onion"], "cilantro": ["parsley"], "lemon juice": ["lime juice"],
           "sour cream": ["greek yogurt"], "basil": ["oregano"]}


@dataclass
class Swap:
    missing: str
    use: str
    note: str = ""


def _allergen_hits(item: str, allergies: set[str]) -> bool:
    return any(item in ALLERGENS.get(a, set()) for a in allergies)


def validate(swaps: list[Swap], *, missing: list[str], pantry: set[str],
             allergies: set[str], tags: list[str]) -> list[Swap]:
    """Return only swaps that are grounded, allergen-safe, and non-toxic."""
    if "safety_critical" in tags:  # canning, raw-egg prep, etc.: never improvise
        return []
    ok = []
    for s in swaps:
        m, u = normalize(s.missing), normalize(s.use)
        if m not in missing:                      # must target a real gap
            continue
        if u not in pantry:                       # grounded in what the user has
            continue
        if u in TOXIC_OR_RISKY or _allergen_hits(u, allergies):
            continue
        ok.append(Swap(m, u, s.note))
    return ok


def curated_swaps(missing: list[str], pantry: set[str]) -> list[Swap]:
    return [Swap(m, u, "from curated table") for m in missing
            for u in CURATED.get(m, []) if u in pantry]
