# Plan

Rule: push to GitHub every day. A public commit history is part of the artifact.

## The question (changed 2026-11-10)

Do current TTS systems read Telugu numbers, dates, currency, phone numbers
and mixed English correctly, and did Eleven v4 improve on Eleven v3?

Why this question: ElevenLabs published an internal text-normalisation
benchmark when v3 left alpha (27 categories, 8 languages, error rate 15.3%
to 4.9%). The languages are not named and nothing comparable is public for
v4. This project runs the same kind of test for Telugu.

Two measurements, reported side by side:

1. **Human verdicts (primary).** A native speaker marks each hard-case clip
   right or wrong on a blind, shuffled listening page.
2. **ASR error rates (secondary).** Calibrated against human FLEURS speech,
   as before. Also answers a side question: how far can an ASR judge be
   trusted for this in Telugu?

## Steps

| # | Do | Done when |
|---|---|---|
| 1 | Repo public, tests green, pipeline run end to end | done |
| 2 | Check the seed rows in `data/hard_cases.csv`; write 10 sentences per category following `data/CATEGORIES.md` | about 120 hard cases |
| 3 | `build_testset.py --n 150`; synthesize `eleven_v3` and `eleven_v4` with the same voice and `apply_text_normalization` left at `auto`; record the voice id in the README | two ElevenLabs systems |
| 4 | Synthesize `mms`, `indic_parler`, `indicf5` (GPU for the last two) | open baselines |
| 5 | `make_listening_page.py --systems ...`; judge every clip; export `verdicts.csv`; `score_listening.py` | `results/listening_report.md` |
| 6 | Transcribe with `whisper_te`, `whisper_v3`, `scribe_v2`; `score.py` | `results/report.md` |
| 7 | Compare: do the ASR scores agree with your verdicts per category? | one table, one paragraph |
| 8 | Write up: README Results, the main finding first, 3 audio examples per failure type | readable in 3 minutes |

## What would make this worth a researcher's click

Whichever of these the data supports:

- a category where v4 still fails in Telugu, with clips
- a category v4 fixed relative to v3 (credit where due)
- ASR-based scoring disagreeing with a native listener

Report what you find, including results that flatter or embarrass any system.

## Known weaknesses to state in the write-up

- One listener. A second native listener on a 50-clip subset would give an
  agreement figure.
- One voice per system; normalisation may differ by voice.
- Hard cases are written by the author, so they reflect one person's idea
  of "typical" Telugu text.

## Later (optional)

Curate Telugu data aimed at the worst category, fine-tune one open model,
and show the before/after on this benchmark.

## Budget

About 120 hard cases + 150 FLEURS sentences, roughly 20k characters per
ElevenLabs model. Check your plan's credit allowance and per-model pricing
before running v4.
