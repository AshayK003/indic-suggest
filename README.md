# Lightweight Romanized-Hindi Correction

**Author:** [Ashay Kushwaha](https://github.com/AshayK003) ([CypherLabs](https://github.com/AshayK003))

> **Status: data pull in progress — no numbers yet.** Nothing below is
> claimed until one command reproduces it. Article follows numbers,
> never precedes them. No ML training anywhere in this project, by design.

---

## Gap

Millions type Hindi in Latin script with no standard spelling (bahut /
bohot / boht / bhot are one word). The field answers with bigger
transformers (IndicXlit, ~11M params, GPU-trained), while classical
Hindi-specific work (Hindex) was built for retrieval query expansion
and normalizers (dhvani) stop at roman-to-roman canonicalization.
**No offline suggestion package corrects noisy romanized Hindi to
ranked Devanagari with a measured accuracy-vs-size table.** This repo
is that package: frequent-word lexicon plus phonetic hashing, weighted
edit distance, and n-gram reranking — counting and rules, zero training.

## What it will do

Suggest top-k Devanagari forms for noisy romanized Hindi input, offline,
in a phone-sized package (~2MB target vs ~44MB transformer). Evaluated
top-1/top-3 on Aksharantar Hindi test (5693 pairs) under a frozen noise
model, with the transformer row cited from its paper and dhvani run live
as the classical rival.

## References

- Aksharantar (Madhani et al., EMNLP 2022): https://arxiv.org/abs/2205.03018
- Aksharantar Hindi data (HF): https://huggingface.co/datasets/ai4bharat/Aksharantar
- IndicXlit (~11M transformer): https://github.com/AI4Bharat/IndicXlit
- Hindex / Weighted Hindex (Hindi phonetic + weighted edit for IR)
- dhvani (IPA-bridge Hinglish normalizer): https://pypi.org/project/dhvani/

## Limitations (honest, updated as numbers land)

- Hindi-first; 20 other languages wait.
- Accuracy ceiling below transformers on rare words — the tradeoff table
  is the point, not a trophy.
- Noise model is synthetic (vowel-drop, confusions); real typing data
  would be better and doesn't exist openly.
