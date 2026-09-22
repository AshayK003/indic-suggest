"""Weighted Levenshtein with phonetic substitution costs (stdlib only).

Costs: insert/delete 1; identical 0; same phonetic group or vowel<->vowel
1; otherwise 2. Operates on raw lowercase chars (phonetic units belong to
the hash stage, not here -- pragmatic split, documented).
"""

from phonetic import GROUPS, VOWELS


def sub_cost(a, b):
    if a == b:
        return 0
    if GROUPS.get(a, a) == GROUPS.get(b, b):
        return 1
    if a in VOWELS and b in VOWELS:
        return 1
    return 2


def weighted_lev(s, t, ins=1, dele=1):
    """Weighted edit distance (DP, O(len(s)*len(t)) time, O(min) rows)."""
    if len(s) < len(t):
        s, t = t, s
        ins, dele = dele, ins
    prev = list(range(len(t) + 1))
    for i, cs in enumerate(s, 1):
        cur = [i] + [0] * len(t)
        for j, ct in enumerate(t, 1):
            cur[j] = min(
                prev[j] + dele,
                cur[j - 1] + ins,
                prev[j - 1] + sub_cost(cs, ct),
            )
        prev = cur
    return prev[len(t)]


def norm_dist(s, t):
    """Length-normalized distance in [0, ~2] for thresholding."""
    if not s and not t:
        return 0.0
    return weighted_lev(s, t) / max(len(s), len(t))
