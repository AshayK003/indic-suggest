# Contributing

## One command reproduces everything

```bash
python -m pytest tests -q   # suite green, hermetic (hand lexicon, no data)
python evaluate.py          # fetches the 33MB Hindi split once if absent, then measures
```

The Aksharantar Hindi split is not committed; `evaluate.py` downloads it
from Hugging Face on first run and caches under `data/` (ignored).

## Corpus policy

Train builds, valid tunes, test scores. Test pairs must never enter the
lexicon — the builder reads train natives only (synthetic romans), and
`evaluate.py` prints the overlap diagnostics every run as the tripwire.

## Ranking rules

New signals (weights, rerankers, G2P improvements) must keep the suite
green and be re-measured on the frozen noise model (seed 20260922).
Beating dhvani means beating 0.113 top-1 on the same noisy inputs —
claims otherwise need the table.

## Open issues (stretch, in order)

1. **Real rule-based transliterator** (schwa deletion, conjuncts, loan
   phonetics) as the scoring engine — the honest v2 this negative
   result motivates.
2. Independent native wordlist to raise the coverage ceiling.
3. Next language (same architecture, new groups).
