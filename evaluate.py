"""One-command evaluation (stdlib + dhvani baseline; no training anywhere).

Builds/loads the freq lexicon, applies the frozen noise model to the test
split, scores top-1/top-3, runs dhvani on the same noisy inputs, and prints
the accuracy-vs-size-vs-latency table. IndicXlit row is cited, never run.

Usage: python evaluate.py
"""

import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from lexicon import bundle_bytes, build, load, save  # noqa: E402
from suggest import suggest  # noqa: E402

DATA = os.path.join(HERE, "data")
TRAIN = os.path.join(DATA, "hin_train.json")
TEST = os.path.join(DATA, "hin_test.json")
BUNDLE = os.path.join(DATA, "lexicon.json")
HF_ZIP = ("https://huggingface.co/datasets/ai4bharat/Aksharantar/"
          "resolve/main/hin.zip")


def ensure_data():
    """One-command reproducibility: fetch hin.zip (33MB, one time) if absent."""
    import urllib.request
    import zipfile

    if os.path.exists(TRAIN) and os.path.exists(TEST):
        return
    os.makedirs(DATA, exist_ok=True)
    zp = os.path.join(DATA, "hin.zip")
    if not os.path.exists(zp):
        print("downloading Aksharantar Hindi split (33MB, one time) ...", flush=True)
        urllib.request.urlretrieve(HF_ZIP, zp)
    with zipfile.ZipFile(zp) as z:
        z.extractall(DATA)
    print("data ready", flush=True)

# Frozen v1 noise model (seeded): vowel-drop + single confusion sub.
VOWELS = set("aeiou")
CONFUSE = {"ph": "f", "v": "b", "sh": "s", "c": "k", "q": "k", "j": "z",
           "au": "o", "ai": "e", "oo": "o", "ee": "i", "aa": "a"}
SEED = 20260922


def noisify(word, rng):
    w = word.lower()
    out = "".join(ch for ch in w if not (ch in VOWELS and rng.random() < 0.30))
    if not out:
        out = w
    for src, dst in CONFUSE.items():
        if src in out and rng.random() < 0.5:
            out = out.replace(src, dst, 1)
            break
    return out or w


def load_pairs(path):
    pairs = []
    with open(path, encoding="utf8") as fh:
        for line in fh:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            roman = (r.get("english word") or "").strip().lower()
            native = (r.get("native word") or "").strip()
            if roman and native:
                pairs.append((roman, native))
    return pairs


def coverage_audit(test):
    """Benchmark-structure diagnostics: test/train overlap on both sides."""
    train_romans, train_nats = set(), set()
    with open(TRAIN, encoding="utf8") as fh:
        for line in fh:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            roman = (r.get("english word") or "").strip().lower()
            native = (r.get("native word") or "").strip()
            if roman:
                train_romans.add(roman)
            if native:
                train_nats.add(native)
    ov_r = sum(1 for r, _ in test if r in train_romans)
    ov_n = sum(1 for _, g in test if g in train_nats)
    print(f"coverage: test romans in train {ov_r}/{len(test)}, "
          f"test natives in train {ov_n}/{len(test)}")
    try:
        import dhvani.lexicon  # noqa
        import glob

        cand = glob.glob(os.path.join(os.path.dirname(dhvani.lexicon.__file__),
                                      "hinglish_lexicon.json"))
        if cand:
            dkeys = set(json.load(open(cand[0], encoding="utf8")))
            hit = sum(1 for r, _ in test if r in dkeys)
            print(f"coverage: test romans as dhvani-lexicon keys {hit}/{len(test)}")
    except Exception as e:
        print(f"dhvani-lexicon coverage skipped: {type(e).__name__}")


def main():
    ensure_data()
    if os.path.exists(BUNDLE):
        bundle = load(BUNDLE)
        print("(lexicon cache hit)")
    else:
        print("building lexicon from train ...", flush=True)
        bundle = build(TRAIN, top_n=50000)
        save(bundle, BUNDLE)
    size_mb = bundle_bytes(bundle) / 1e6
    print(f"lexicon entries: {len(bundle['lex'])}, bundle: {size_mb:.2f} MB")

    test = load_pairs(TEST)
    coverage_audit(test)
    rng = random.Random(SEED)
    noisy = [(noisify(roman, rng), native) for roman, native in test]
    changed = sum(1 for (n, _), (r, _) in zip(noisy, test) if n != r)
    print(f"test pairs: {len(test)}, noised: {changed} ({changed / len(test):.0%})")

    t0 = time.perf_counter()
    top1 = top3 = 0
    for roman, gold in noisy:
        sug = suggest(roman, bundle, k=3)
        if sug and sug[0] == gold:
            top1 += 1
        if gold in sug:
            top3 += 1
    dt = time.perf_counter() - t0
    n = len(noisy)
    print(f"ours: top-1 {top1}/{n} = {top1 / n:.3f}   top-3 {top3}/{n} = {top3 / n:.3f}")
    print(f"latency: {dt / n * 1000:.2f} ms/query ({n} queries, {dt:.0f}s total)")

    try:
        import dhvani

        t0 = time.perf_counter()
        hits = sum(1 for roman, gold in noisy if dhvani.to_devanagari(roman) == gold)
        ddt = time.perf_counter() - t0
        print(f"dhvani to_devanagari: {hits}/{n} = {hits / n:.3f} "
              f"({ddt / n * 1000:.2f} ms/query)")
    except Exception as e:
        print(f"dhvani baseline skipped: {type(e).__name__}: {e}")

    print("IndicXlit (CITED, not run): 60.56 top-1 on Dakshina-hi "
          "(different test set; directional comparison only), ~11M params (~44MB fp32)")


if __name__ == "__main__":
    main()
