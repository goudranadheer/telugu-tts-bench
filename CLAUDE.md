# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A benchmark of Telugu TTS intelligibility whose main point is that the usual metric is untrustworthy: Telugu ASR is weak, so a raw ASR-based error rate mostly measures the ASR judge, not the TTS. Every design choice follows from that (human-speech calibration row, several judges, akshara-level scoring). `PLAN.md` is the day-by-day plan and says which result framings matter; `README.md` "Results" is filled in last.

Status: the pipeline has run end to end once, on CPU, with `mms` + `whisper_te_small` on a small subset (`results/pipeline_check.md`; a check, not a result). `build_testset.py`, the `MMS` adapter and `HFWhisper` are known to work. The ElevenLabs, Indic Parler, IndicF5 and Scribe adapters are still unrun, so expect to fix API details on first use.

## Commands

```bash
python -m pytest                              # all tests (stdlib + pytest only)
python -m pytest tests/test_core.py::test_name   # single test

pip install -r requirements.txt               # heavy deps, only for synthesis/transcription
python scripts/build_testset.py --n 150       # -> data/testset.csv, audio/human/
python scripts/synthesize.py --system mms     # -> audio/<system>/<id>.<ext>, timing.jsonl
python scripts/transcribe.py --judge whisper_te   # appends results/transcripts.jsonl
python scripts/score.py --unit akshara        # -> results/report.md, results/failures.csv
```

On this machine the interpreter is `python3` (there is no `python` on PATH).

Scripts are run from the repo root as plain files; they add the root to `sys.path` themselves. There is no installable package and no linter config.

Environment variables: `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` (ElevenLabs TTS and Scribe), `INDICF5_REF_AUDIO`, `INDICF5_REF_TEXT` (IndicF5 reference clip). `indic_parler` is gated on Hugging Face and needs a logged-in token. `indic_parler` and `indicf5` need extra git installs listed as comments in `requirements.txt`; IndicF5 wants its own venv.

## Architecture

A four-stage pipeline joined only by files on disk, so each stage can run on a different machine (CPU laptop, Colab GPU) and be resumed:

1. `build_testset.py` samples FLEURS Telugu test sentences (saving the human recordings to `audio/human/`) and appends `data/hard_cases.csv`. Output rows are `id, category, text, spoken`.
2. `synthesize.py` looks up one entry in `SYSTEMS` and writes one audio file per test-set id.
3. `transcribe.py` looks up one entry in `JUDGES` and transcribes **every** folder under `audio/`, including `human`. A system is identified purely by its folder name.
4. `score.py` joins transcripts to the test set by `id` and produces the report.

Things that are easy to get wrong:

- **`text` vs `spoken`.** TTS receives `text`; scoring compares the ASR hypothesis against `spoken` (digits and English words written out in Telugu). This is what makes text-normalisation failures count as errors. In `hard_cases.csv` an empty `spoken` means "same as `text`".
- **`human` is not a TTS system.** It is the per-judge error floor from real speech. `score.py` reports it in the main table but excludes it from pairwise significance tests. TTS numbers are only meaningful relative to it.
- **Both sides are normalised.** `metrics.edit_counts` runs reference and hypothesis through `normalize.normalize` before tokenising, so any change to normalisation changes every score.
- **Error rates are corpus-level** (total edits / total reference length), and the bootstrap resamples sentences as `(edits, ref_len)` pairs, not per-sentence rates. `paired_bootstrap` requires both systems' pairs in the same sentence order.
- **Aksharas** (`normalize.aksharas`) are orthographic syllables: a virama-joined consonant cluster plus vowel sign and modifiers is one unit. This is the default scoring unit because Telugu is agglutinative and word error rate over-penalises a single wrong suffix.
- **Scoring must stay dependency-free.** `ttsbench/metrics.py`, `normalize.py`, `stats.py` and `score.py` use only the standard library; adapters import torch/transformers/requests inside their classes for that reason.
- **Resumability.** `synthesize.py` skips ids whose audio file exists; `transcribe.py` skips `(id, system, judge)` keys already in `transcripts.jsonl`. To redo something, delete the file or the lines. Synthesis failures are logged to `timing.jsonl` and skipped, not raised.
- **Adding a system or judge** means a class with `synthesize(text, out)` plus an `ext` attribute, or `transcribe(path)`, registered in the `SYSTEMS` / `JUDGES` dict.
- **Old Whisper fine-tunes** (`vasista22/*`) ship a generation config that current transformers rejects when a language is passed; `HFWhisper(model_id, gen_config_from=...)` borrows the matching OpenAI base config. Any new Whisper fine-tune judge may need the same.
- **CPU speed.** `whisper_te_small` takes roughly 40 s per FLEURS clip on 2 CPU cores; use a GPU for full runs and the large judges.
- **`scribe_v2` is an ElevenLabs model**, so it must never be the only judge reported for ElevenLabs TTS.

`audio/`, `data/testset.csv` and `results/transcripts.jsonl` are gitignored; `results/report.md` and `results/failures.csv` are meant to be committed.

## Working conventions from the plan

- Report what the data shows, including results unflattering to any system, always with confidence intervals.
- The seed rows in `data/hard_cases.csv` were machine-written and need a native speaker's check; do not treat them as verified references.
- ElevenLabs synthesis spends credits (about 17k characters per model for the full set), so do not re-run it casually.
