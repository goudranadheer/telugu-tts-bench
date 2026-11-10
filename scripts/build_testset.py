"""Build data/testset.csv and the human reference audio.

Two parts:
  1. `fleurs`  - N sentences sampled from the FLEURS Telugu test split, with
                 the human recording saved to audio/human/<id>.wav. These
                 calibrate each ASR judge (its error on real speech).
  2. `hard`    - your hand-written hard cases from data/hard_cases.csv.

Usage: python scripts/build_testset.py --n 150
NOTE: not run when the scaffold was written.
"""
import argparse
import csv
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    import soundfile as sf
    from datasets import load_dataset

    ds = load_dataset("google/fleurs", "te_in", split="test")
    seen, idx = set(), []
    for i, text in enumerate(ds["transcription"]):  # one recording per sentence
        if text not in seen:
            seen.add(text)
            idx.append(i)
    random.Random(args.seed).shuffle(idx)

    human = ROOT / "audio" / "human"
    human.mkdir(parents=True, exist_ok=True)
    rows = []
    for k, i in enumerate(sorted(idx[: args.n])):
        ex = ds[i]
        sid = f"fleurs_{k:03d}"
        sf.write(human / f"{sid}.wav", ex["audio"]["array"], ex["audio"]["sampling_rate"])
        rows.append({"id": sid, "category": "fleurs", "text": ex["raw_transcription"],
                     "spoken": ex["transcription"]})

    with open(ROOT / "data" / "hard_cases.csv", encoding="utf-8") as f:
        for k, r in enumerate(csv.DictReader(f)):
            rows.append({"id": f"hard_{k:03d}", "category": r["category"],
                         "text": r["text"], "spoken": r["spoken"] or r["text"]})

    with open(ROOT / "data" / "testset.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "category", "text", "spoken"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} sentences")


if __name__ == "__main__":
    main()
