"""Transcribe every audio folder with one ASR judge. Resumable.

Usage: python scripts/transcribe.py --judge whisper_te
Appends to results/transcripts.jsonl: {id, system, judge, hyp}
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ttsbench.asr import JUDGES  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", required=True, choices=sorted(JUDGES))
    args = ap.parse_args()

    out = ROOT / "results" / "transcripts.jsonl"
    out.parent.mkdir(exist_ok=True)
    done = set()
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            d = json.loads(line)
            done.add((d["id"], d["system"], d["judge"]))

    judge = JUDGES[args.judge]()
    with open(out, "a", encoding="utf-8") as f:
        for sys_dir in sorted(p for p in (ROOT / "audio").iterdir() if p.is_dir()):
            for wav in sorted(sys_dir.glob("*.wav")) + sorted(sys_dir.glob("*.mp3")):
                key = (wav.stem, sys_dir.name, args.judge)
                if key in done:
                    continue
                hyp = judge.transcribe(wav)
                f.write(json.dumps({"id": wav.stem, "system": sys_dir.name,
                                    "judge": args.judge, "hyp": hyp},
                                   ensure_ascii=False) + "\n")
                f.flush()
                print(*key)


if __name__ == "__main__":
    main()
