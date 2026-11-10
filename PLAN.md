# 10-day plan

Rule: push to GitHub every day. A public commit history is part of the artifact.

| Day | Do | Done when |
|---|---|---|
| 1 | Create the public repo, push this scaffold, run `pytest`. Get an ElevenLabs API key and a Hugging Face token; accept the Indic Parler-TTS terms. | Tests green on your machine, repo public |
| 2 | Run `build_testset.py`. Synthesize with `mms` (CPU is enough). Transcribe with `whisper_te`. Run `score.py`. Fix whatever breaks in the adapters. | One full row in `report.md`, end to end |
| 3 | Write 20 sentences each for `numbers`, `codemix`, `conjuncts` in `data/hard_cases.csv`. Check the 7 seed rows: they were machine-written and need a native speaker's eye. | 60+ hard cases |
| 4 | Synthesize `eleven_v3` and `eleven_flash_v2_5`. Pick one stock voice and record its id in the README. | Two more systems |
| 5 | Synthesize `indic_parler` and `indicf5` on a GPU (Colab works). | All five systems |
| 6 | Transcribe everything with `whisper_v3` and `scribe_v2`. Re-score. | Three judges x six audio sets |
| 7 | Calibration analysis: human-speech floor per judge, and do the judges rank the systems the same way? | One paragraph and one table |
| 8 | Listen to the 30 worst rows per system in `failures.csv`. Tag each: real TTS error, ASR error, or reference error. | Tagged sheet, error-type counts |
| 9 | Small human check: 20 sentences x all systems, 5 native listeners, 1-5 naturalness. A shared form is enough. | Mean score per system |
| 10 | Write up: fill README Results, lead with the one finding that surprised you, add 3 audio examples. | README someone can read in 3 minutes |

## What makes this worth a recruiter's click

Not "ElevenLabs scored X". The interesting result is one of these, whichever
the data supports:

- how much of a Telugu TTS error score is really the ASR judge's own error
- a category where every system fails (digits and code-mixing are likely)
- judges disagreeing on which system is best

Report what you find, including results that are unflattering to any system.

## Week 2 (optional, stronger)

Fine-tune one open model on Telugu data and re-run the same benchmark to show
a measured before/after. Only start once the day-10 write-up is public.

## Budget

Test set is roughly 210 sentences, about 80 characters each: around 17k
characters per ElevenLabs model. Check your plan's credit allowance first.
