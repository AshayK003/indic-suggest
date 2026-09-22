"""Frequent-word lexicon + phonetic index from Aksharantar JSONL (stdlib).

Split discipline: train builds, valid tunes weights, test scores. Test
pairs must never enter the lexicon -- enforced by building only from the
train file passed in.
"""

import json
from collections import Counter

from phonetic import code


def build(train_path, top_n=150000):
    """Lexicon v2 (pivot 2026-09-22): keys are SYNTHETIC romans generated
    from train natives, because the test vocab is disjoint from train romans
    by construction (a train-roman lookup scores ~0). No test pairs enter:
    test romans are never read here, only train natives.

    Returns dict with lex {synthetic-roman: native}, index, bigrams, counts.
    Collisions (two natives, one roman) go to the more frequent native and
    are counted, not hidden."""
    import math

    from romanize import romanize

    natfreq = Counter()
    with open(train_path, encoding="utf8") as fh:
        for line in fh:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            native = (r.get("native word") or "").strip()
            if native:
                natfreq[native] += 1
    kept_natives = [w for w, _ in natfreq.most_common(top_n)]
    lex, collisions = {}, 0
    for w in kept_natives:
        r = romanize(w).lower()
        if not r:
            continue
        if r in lex:
            collisions += 1
            continue
        lex[r] = w
    index = {}
    for w, native in lex.items():
        index.setdefault(code(w), []).append((w, native))
    bigrams = Counter()
    for w in lex:
        padded = f"^{w}$"
        for i in range(len(padded) - 1):
            bigrams[padded[i : i + 2]] += 1
    total = sum(bigrams.values())
    logprob = {b: math.log(c / total) for b, c in bigrams.items()}
    return {"lex": lex, "index": index, "bigrams": logprob,
            "counts": {"natives_kept": len(kept_natives),
                       "lex_entries": len(lex), "collisions": collisions}}


def save(bundle, path):
    with open(path, "w", encoding="utf8") as fh:
        json.dump(bundle, fh, ensure_ascii=False)


def load(path):
    with open(path, encoding="utf8") as fh:
        return json.load(fh)


def bundle_bytes(bundle):
    import json as _j

    return len(_j.dumps(bundle, ensure_ascii=False).encode("utf8"))
