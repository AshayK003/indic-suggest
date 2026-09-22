"""The one runnable check (SPEC): hand-lexicon correction, G2P fallback,
edit-distance units. Hermetic: no network, no dataset."""

from edit import norm_dist, weighted_lev
from lexicon import build as _build  # noqa: F401 (API surface check)
from phonetic import code, same_group
from suggest import g2p, normalize, suggest

LEX = {
    "bohot": ["बोहोत"], "boht": ["बोहत"], "bahut": ["बहुत"], "bhot": ["भोत"],
    "kese": ["कैसे"], "kaise": ["कैसे"], "ho": ["हो"],
    "tum": ["तुम"], "tumhe": ["तुम्हें"], "kya": ["क्या"],
}

BUNDLE = {"lex": LEX, "index": {}, "bigrams": {}}


def _index():
    from collections import defaultdict

    idx = defaultdict(list)
    for roman, natives in LEX.items():
        for native in natives:
            idx[code(roman)].append((roman, native))
    return {"lex": LEX, "index": dict(idx), "bigrams": {}}


def test_phonetic_buckets_variants():
    assert code("bohot") == code("boht") == code("bahut") == "bHT"
    # "bhot" folds bh->P (correct: bhot spells bhot, not bohot) -- own bucket
    assert code("bhot") == "PT"
    assert code("kese") == code("kaise")
    assert same_group("b", "v") and same_group("k", "q")
    assert not same_group("k", "s")


def test_correction_top1():
    b = _index()
    assert suggest("boht", b, k=3)[0] == "बोहत"
    assert suggest("bhot", b, k=3)[0] == "भोत"
    assert "कैसे" in suggest("kese", b, k=3)


def test_edit_units():
    assert weighted_lev("kese", "kaise") < weighted_lev("kese", "kutta")
    assert weighted_lev("bohot", "bohot") == 0
    assert 0.0 <= norm_dist("abc", "abd") <= 2.0


def test_normalize_and_g2p_fallback():
    assert normalize("Bohotttt") == ["bohotttt", "bohott", "bohot"]
    got = g2p("xyzq")
    assert isinstance(got, str) and len(got) > 0
    assert suggest("zzzqqq", _index(), k=1) == [g2p("zzzqqq")]
