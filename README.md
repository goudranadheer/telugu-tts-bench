# telugu-tts-bench

Do current TTS systems read Telugu numbers, dates, currency and mixed
English correctly? And can an automatic metric tell?

**Status: pipeline runs end to end; no benchmark results yet.** One system
(`mms`) and one small CPU judge have been run on a handful of sentences as a
pipeline check (`results/pipeline_check.md`). The other adapters are unrun.

## The question

Turning "₹450" or "9848022338" into the right spoken words is a known weak
spot of TTS systems. ElevenLabs reported an internal benchmark of it for
Eleven v3 (27 categories, 8 unnamed languages); we found no public figures for Telugu
or Eleven v4.

This benchmark measures it for Telugu in two ways:

1. **Human verdicts.** A native speaker marks each clip right or wrong on a
   blind, shuffled listening page. This is the primary result.
2. **ASR error rates.** The usual automatic metric: transcribe the synthetic
   speech and count errors. Telugu ASR is weak (public models report roughly
   40-50% word error on real FLEURS speech), so every ASR judge is first
   calibrated on human recordings, several judges are used, and scoring is
   done in aksharas (orthographic syllables) as well as words.

Comparing the two shows how far the automatic metric can be trusted.

## Test set

| Part | Size | Purpose |
|---|---|---|
| `fleurs` | 150 sentences from the FLEURS Telugu test split | General text, with human audio to calibrate the ASR judges |
| hard cases | about 10 per category, hand-written | Phone numbers, currency, dates, times, quantities, percentages, units, maths, emails, alphanumeric codes, code-mixing, plus a control set |

Categories and judging rules: `data/CATEGORIES.md`.

Each row has `text` (what the TTS receives) and `spoken` (the verbalised
reference, e.g. digits written out), so text-normalisation failures count
as errors.

## Systems

| Key | System |
|---|---|
| `eleven_v4`, `eleven_v3`, `eleven_flash_v2_5` | ElevenLabs API |
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
python scripts/make_listening_page.py --systems eleven_v3 eleven_v4 mms
# judge the clips in results/listening/index.html, export verdicts.csv there
python scripts/score_listening.py
```

`score_listening.py` writes `results/listening_report.md`: share of sentences
read wrong per system and category, with Wilson intervals and exact McNemar
tests. `score.py` writes `results/report.md` (ASR error rates with bootstrap
intervals and paired tests) and `results/failures.csv`.

Tests: `python -m pytest`

## Results

Pending.

## Limitations

- One listener judges the clips; verdicts are blind to the system but not independent of the listener.
- Neither measure covers naturalness or prosody.
- `scribe_v2` is an ElevenLabs model, so it is never the only judge for
  ElevenLabs TTS.
- FLEURS text may appear in some systems' training data.
- One voice per system; results can differ by voice.
