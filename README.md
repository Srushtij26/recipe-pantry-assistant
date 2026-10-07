# 🥕 Recipe Pantry Assistant

Type what's in your fridge, get recipes ranked by how many ingredients you already have,
plus LLM-suggested swaps for what's missing, **filtered through a safety layer**.

## How it works
1. `matcher.py`: normalizes ingredients (plurals, aliases) and ranks recipes by coverage. Deterministic, no LLM.
2. `llm.py`: asks Claude to propose swaps as strict JSON.
3. `guardrails.py`: validates every proposal before the user sees it.

## Guardrails
| Rule | Why |
|---|---|
| Swap must use an ingredient the user actually has | Prevents invented ingredients |
| Declared allergens always block a swap | Allergy safety |
| Toxic/risky items denylisted | Prevents harmful suggestions |
| `safety_critical` recipes (canning, raw egg) get no swaps | Where improvising is dangerous |
| LLM failure or malformed JSON falls back to a curated table | Graceful degradation |

## Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your key
streamlit run app.py
pytest
```

## Roadmap
- Larger recipe dataset (e.g. Recipe1M subset) and fuzzy/embedding ingredient matching
- Eval set of tricky swap prompts to measure guardrail catch rate
- Quantity-aware matching
