from pantry.guardrails import Swap, validate
from pantry.matcher import load_recipes, parse_pantry, rank

KW = dict(missing=["butter"], pantry={"olive oil", "milk"}, allergies=set(), tags=[])


def test_ranking_prefers_more_matches():
    r = rank(parse_pantry("egg, tomato, onion, butter, cheese"), load_recipes())
    assert r[0].name == "Veggie Omelette" and r[0].score == 1.0


def test_normalizes_plurals_and_aliases():
    assert parse_pantry("Tomatoes, scallions") == {"tomato", "green onion"}


def test_valid_swap_passes():
    assert validate([Swap("butter", "olive oil")], **KW)


def test_swap_not_in_pantry_rejected():
    assert not validate([Swap("butter", "ghee")], **KW)


def test_allergen_swap_rejected():
    assert not validate([Swap("butter", "milk")], **{**KW, "allergies": {"dairy"}})


def test_safety_critical_never_swapped():
    assert not validate([Swap("butter", "olive oil")], **{**KW, "tags": ["safety_critical"]})


def test_toxic_rejected():
    kw = {**KW, "pantry": {"raw kidney bean"}}
    assert not validate([Swap("butter", "raw kidney beans")], **kw)
