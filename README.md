# telugu-tts-bench

How well do current TTS systems speak Telugu, and can we trust the numbers
we use to measure that?

**Status: scaffold. No results yet.** The scoring code is tested; the model
adapters have not been run.

## The question

TTS intelligibility is usually measured by transcribing the synthetic speech
with an ASR model and counting errors. That works in English, where ASR is
near-perfect. Telugu ASR is not: public models report word error rates of
roughly 40-50% on real FLEURS speech. A raw "WER of system X" in Telugu
therefore mostly measures the ASR, not the TTS.

This benchmark does three things about that:

1. **Calibrates every ASR judge on human speech.** The same sentences are
   scored on real FLEURS recordings, which gives each judge's error floor.
2. **Uses several judges** and reports where they agree and disagree.
3. **Scores in aksharas** (orthographic syllables) as well as words, because
   Telugu is agglutinative and one wrong suffix makes a whole long word wrong.

## Test set

| Part | Size | Purpose |
|---|---|---|
| `fleurs` | 150 sentences from the FLEURS Telugu test split | General text, with human audio for calibration |
| `numbers` | hand-written | Digits, currency, dates |
| `codemix` | hand-written | English words inside Telugu sentences |
| `conjuncts` | hand-written | Dense consonant clusters |

Each row has `text` (what the TTS receives) and `spoken` (the verbalised
reference, e.g. digits written out), so text-normalisation failures count
as errors.

## Systems

| Key | System |
|---|---|
| `eleven_v3`, `eleven_flash_v2_5` | ElevenLabs API |
| `indic_parler` | AI4Bharat Indic Parler-TTS |
| `indicf5` | AI4Bharat IndicF5 |
| `mms` | Meta MMS-TTS Telugu |
| `human` | FLEURS recordings (reference, not a TTS) |

## Run

```bash
pip install -r requirements.txt
python scripts/build_testset.py --n 150
python scripts/synthesize.py --system mms          # repeat per system
python scripts/transcribe.py --judge whisper_te    # repeat per judge
python scripts/score.py --unit akshara
```

`score.py` writes `results/report.md` (overall and per-category error rates
with bootstrap 95% confidence intervals and paired significance tests) and
`results/failures.csv` (every utterance, worst first, for error analysis).

Tests: `python -m pytest`

## Results

Pending.

## Limitations

- ASR-based scores measure intelligibility only, not naturalness or prosody.
- `scribe_v2` is an ElevenLabs model, so it is never the only judge for
  ElevenLabs TTS.
- FLEURS text may appear in some systems' training data.
- One voice per system; results can differ by voice.
