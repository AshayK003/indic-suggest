"""Suggestion pipeline: normalize -> phonetic bucket -> weighted-edit rank
-> bigram rerank -> top-k + deterministic G2P fallback (stdlib only)."""

import math
import re

from edit import weighted_lev
from phonetic import code

# Crude deterministic roman->Devanagari fallback (no retroflex split, no
# schwa deletion). Job: never return empty, not be correct. Documented.
G2P = {
    "aa": "आ", "ee": "ई", "oo": "ऊ", "ai": "ऐ", "au": "औ",
    "kh": "ख", "gh": "घ", "ch": "छ", "jh": "झ", "th": "थ", "dh": "ध",
    "ph": "फ", "bh": "भ", "sh": "श",
    "a": "अ", "e": "ए", "i": "इ", "o": "ओ", "u": "उ",
    "k": "क", "g": "ग", "c": "क", "q": "क", "j": "ज", "z": "ज़",
    "t": "त", "d": "द", "n": "न", "p": "प", "f": "फ़", "b": "ब",
    "v": "व", "w": "व", "m": "म", "y": "य", "r": "र", "l": "ल",
    "s": "स", "x": "क्स", "h": "ह",
}


def g2p(word):
    """Greedy digraph-first transliteration. Deterministic, crude."""
    out, i = [], 0
    word = word.lower()
    while i < len(word):
        two = word[i : i + 2]
        if two in G2P and len(two) == 2 and two in (
            "aa", "ee", "oo", "ai", "au", "kh", "gh", "ch", "jh",
            "th", "dh", "ph", "bh", "sh",
        ):
            out.append(G2P[two])
            i += 2
        elif word[i] in G2P:
            out.append(G2P[word[i]])
            i += 1
        else:
            out.append(word[i])
            i += 1
    return "".join(out)


def normalize(word):
    """Lowercase + repeat handling. Returns query variants to try in order:
    runs of 3+ collapsed to 2 (keeps legit doubles like dilli), then to 1."""
    w = word.lower().strip()
    w2 = re.sub(r"(.)\1{2,}", r"\1\1", w)
    w1 = re.sub(r"(.)\1+", r"\1", w)
    variants = [w]
    if w2 != w:
        variants.append(w2)
    if w1 != w2:
        variants.append(w1)
    return variants


def bigram_score(roman, logprob):
    """Mean log-prob of roman bigrams (common spellings preferred)."""
    padded = f"^{roman}$"
    scores = [logprob.get(padded[i : i + 2], -12.0) for i in range(len(padded) - 1)]
    return sum(scores) / max(len(scores), 1)


def suggest(query_word, bundle, k=3):
    """Top-k native suggestions [(native, dist)]. G2P fallback if bucket empty."""
    lex, index, logprob = bundle["lex"], bundle["index"], bundle["bigrams"]
    best = {}
    for q in normalize(query_word):
        for roman, native in index.get(code(q), []):
            d = weighted_lev(q, roman)
            key = (native, roman)
            if key not in best or d < best[key][0]:
                best[key] = (d, bigram_score(roman, logprob))
    ranked = sorted(best.items(), key=lambda kv: (kv[1][0], -kv[1][1], kv[0][0]))
    out, seen = [], set()
    for (native, _roman), (_d, _s) in ranked:
        if native not in seen:
            seen.add(native)
            out.append(native)
        if len(out) == k:
            break
    if not out:
        out = [g2p(normalize(query_word)[0])]
    return out
