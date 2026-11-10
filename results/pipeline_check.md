# Pipeline check (not a benchmark result)

First end-to-end run, 2026-11-10. Purpose: prove that test-set build,
synthesis, transcription and scoring work together. The sample is far too
small to rank anything.

- System: `mms` (Meta MMS-TTS Telugu), plus `human` FLEURS recordings
- Judge: `whisper_te_small` (vasista22/whisper-telugu-small, CPU)
- Sentences: 12 FLEURS (human and mms) + the 7 seed hard cases (mms only)

| System | Unit | n | Overall | 95% CI | fleurs | numbers | codemix | conjuncts |
|---|---|---|---|---|---|---|---|---|
| human | akshara | 12 | 12.3 | 8.7-16.7 | 12.3 | | | |
| mms | akshara | 19 | 27.0 | 20.2-34.5 | 22.8 | 71.8 | 56.5 | 0.0 |
| human | word | 12 | 30.7 | 25.5-36.1 | 30.7 | | | |
| mms | word | 19 | 35.9 | 29.1-42.7 | 32.0 | 71.4 | 60.0 | 0.0 |

## Things to check on the full run

These are observations from a tiny sample, to be confirmed or rejected:

1. On real human speech this judge already shows about 12% akshara error and
   about 31% word error. That is the floor any TTS score has to be read against.
2. By word error rate, human speech (30.7) and MMS (32.0) look almost the
   same on FLEURS sentences; by akshara error rate they separate (12.3 vs
   22.8). The scoring unit may matter as much as the system.
3. MMS appears to skip digits and Latin-script words entirely. For
   "ఈ పుస్తకం ధర ₹450." the judge heard "ఈ పుస్తకం తా"; for
   "రేపు meeting ని postpone చేద్దాం." it heard "రేపు నీ చేద్దాం". Listen to
   the audio to confirm this is the TTS and not the judge.
4. The two conjunct-heavy seed sentences were transcribed perfectly.

The seed hard cases have not yet been checked by a native speaker.
