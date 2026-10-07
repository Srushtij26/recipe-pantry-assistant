"""Deterministic ingredient normalization and recipe ranking (no LLM)."""
import json
import re
from dataclasses import dataclass
from pathlib import Path

STAPLES = {"salt", "pepper", "water", "oil"}  # assumed on hand
ALIASES = {"scallion": "green onion", "spring onion": "green onion",
           "capsicum": "bell pepper", "coriander": "cilantro",
           "chickpeas": "chickpea", "garbanzo bean": "chickpea"}


def normalize(item: str) -> str:
    s = re.sub(r"[^a-z ]", "", item.lower()).strip()
    if s.endswith("ies"):
        s = s[:-3] + "y"
    elif s.endswith("oes"):
        s = s[:-2]
    elif s.endswith("s") and not s.endswith("ss"):
        s = s[:-1]
    return ALIASES.get(s, s)


def parse_pantry(text: str) -> set[str]:
    return {normalize(p) for p in re.split(r"[,\n;]", text) if p.strip()}


@dataclass
class Match:
    name: str
    have: list[str]
    missing: list[str]
    tags: list[str]

    @property
    def score(self) -> float:
        total = len(self.have) + len(self.missing)
        return len(self.have) / total if total else 0.0


def load_recipes(path: str | Path = "data/recipes.json") -> list[dict]:
    return json.loads(Path(path).read_text())


def rank(pantry: set[str], recipes: list[dict]) -> list[Match]:
    have_all = pantry | STAPLES
    out = []
    for r in recipes:
        ings = [normalize(i) for i in r["ingredients"]]
        have = [i for i in ings if i in have_all]
        missing = [i for i in ings if i not in have_all]
        if have:
            out.append(Match(r["name"], have, missing, r.get("tags", [])))
    return sorted(out, key=lambda m: (-m.score, len(m.missing), m.name))
