"""Devanagari-tuned phonetic hashing for romanized Hindi (rules, not ML).

Pipeline: lowercase -> greedy digraph fold -> first letter kept, rest mapped
to articulation groups with vowels dropped and repeat codes collapsed
(Soundex-style, but with Hindi-appropriate groups). A prefilter: high
recall by design, precision left to weighted edit distance.

    bohot / boht / bahut / bhot  ->  bHT
    kese / kaise                  ->  kS
"""

DIGRAPHS = {
    "kh": "K", "gh": "G", "ch": "C", "jh": "J", "th": "T", "dh": "T",
    "ph": "P", "bh": "P", "sh": "S", "aa": "A", "ee": "I", "oo": "U",
    "ai": "E", "au": "O", "ou": "U", "ng": "N", "ny": "N",
}

GROUPS = {
    "a": "a", "A": "A", "e": "e", "E": "E", "i": "i", "I": "I",
    "o": "o", "O": "O", "u": "u", "U": "U",
    "k": "K", "c": "K", "q": "K", "g": "G",
    "j": "J", "z": "J",
    "t": "T", "d": "T", "n": "N",
    "p": "P", "f": "P", "b": "P", "v": "P", "w": "P",
    "m": "M", "y": "Y", "r": "R", "l": "L",
    "s": "S", "x": "S", "h": "H",
}

VOWELS = set("aeiouAEIOU")


def fold(word):
    """Greedy left-to-right digraph fold. Returns unit list."""
    word = word.lower()
    units, i = [], 0
    while i < len(word):
        two = word[i : i + 2]
        if two in DIGRAPHS:
            units.append(DIGRAPHS[two])
            i += 2
        else:
            units.append(word[i])
            i += 1
    return units


def code(word):
    """Phonetic code: first unit raw + grouped consonant classes, collapsed."""
    units = fold(word)
    if not units:
        return ""
    out = [units[0]]
    for u in units[1:]:
        if u in VOWELS:
            continue
        g = GROUPS.get(u, u)
        if g != out[-1]:
            out.append(g)
    return "".join(out)


def same_group(a, b):
    """Single-char phonetic equivalence for edit costs."""
    if a == b:
        return True
    return GROUPS.get(a, a) == GROUPS.get(b, b)
