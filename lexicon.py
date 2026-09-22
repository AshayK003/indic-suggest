"""Frequent-word lexicon + phonetic index from Aksharantar JSONL (stdlib).

Split discipline: train builds, valid tunes weights, test scores. Test
pairs must never enter the lexicon -- enforced by building only from the
train file passed in.
"""

import json
from collections import Counter

from phonetic import code


def build(train_path, top_n=50000):
    """Returns dict with lex {roman: native}, index {code: [(roman, native)]},
    bigrams {bigram: log-prob} over kept romans, and counts."""
    import math

    freq = Counter()
    native_of = {}
    with open(train_path, encoding="utf8") as fh:
        for line in fh:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            roman = (r.get("english word") or "").strip().lower()
            native = (r.get("native word") or "").strip()
            if not roman or not native:
                continue
            freq[roman] += 1
            native_of.setdefault(roman, Counter())[native] += 1
    kept = [w for w, _ in freq.most_common(top_n)]
    lex = {w: native_of[w].most_common(1)[0][0] for w in kept}
    index = {}
    for w in kept:
        index.setdefault(code(w), []).append((w, lex[w]))
    bigrams = Counter()
    for w in kept:
        padded = f"^{w}$"
        for i in range(len(padded) - 1):
            bigrams[padded[i : i + 2]] += 1
    total = sum(bigrams.values())
    logprob = {b: math.log(c / total) for b, c in bigrams.items()}
    return {"lex": lex, "index": index, "bigrams": logprob,
            "counts": {"train_rows_kept": len(kept)}}


def save(bundle, path):
    with open(path, "w", encoding="utf8") as fh:
        json.dump(bundle, fh, ensure_ascii=False)


def load(path):
    with open(path, encoding="utf8") as fh:
        return json.load(fh)


def bundle_bytes(bundle):
    import json as _j

    return len(_j.dumps(bundle, ensure_ascii=False).encode("utf8"))
