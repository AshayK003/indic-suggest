"""Deterministic native-to-roman generator (rules, not ML).

One canonical roman per Devanagari word (ITRANS-flavored): used to
synthesize lexicon keys from train natives. Crude by design (no schwa
deletion, dental/retroflex merged where roman rarely distinguishes);
the phonetic bucket + edit distance absorb the mismatch -- that
absorption is the product, not a bug.
"""

MAP = {
    "अ": "a", "आ": "aa", "इ": "i", "ई": "ee", "उ": "u", "ऊ": "oo",
    "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au", "अं": "an", "अः": "ah",
    "ा": "aa", "ि": "i", "ी": "ee", "ु": "u", "ू": "oo",
    "े": "e", "ै": "ai", "ो": "o", "ौ": "au", "ं": "n", "ँ": "n",
    "ः": "h", "्": "",
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "ng",
    "च": "c", "छ": "ch", "ज": "j", "झ": "jh", "ञ": "ny",
    "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh", "ण": "n",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
    "य": "y", "र": "r", "ल": "l", "व": "v",
    "श": "sh", "ष": "sh", "स": "s", "ह": "h",
    "क्ष": "ksh", "त्र": "tr", "ज्ञ": "gy",
    "क़": "q", "ख़": "kh", "ग़": "g", "ज़": "z", "फ़": "f",
    "ड़": "r", "ढ़": "rh", "़": "",
    "ॉ": "o", "ॆ": "e", "ॐ": "om", "।": ".", "॥": "..",
    "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
    "५": "5", "६": "6", "७": "7", "८": "8", "९": "9",
}


def romanize(word):
    """Greedy longest-match transliteration. Unknown chars pass through."""
    out, i = [], 0
    while i < len(word):
        three = word[i : i + 3]
        two = word[i : i + 2]
        if three in MAP:
            out.append(MAP[three])
            i += 3
        elif two in MAP:
            out.append(MAP[two])
            i += 2
        elif word[i] in MAP:
            out.append(MAP[word[i]])
            i += 1
        else:
            out.append(word[i])
            i += 1
    return "".join(out)
