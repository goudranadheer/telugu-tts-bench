"""Synthesize the whole test set with one system. Resumable.

Usage: python scripts/synthesize.py --system mms
Writes audio/<system>/<id>.<ext> and audio/<system>/timing.jsonl
"""
import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ttsbench.systems import SYSTEMS, timed  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True, choices=sorted(SYSTEMS))
    args = ap.parse_args()

    system = SYSTEMS[args.system]()
    out_dir = ROOT / "audio" / args.system
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(ROOT / "data" / "testset.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    with open(out_dir / "timing.jsonl", "a", encoding="utf-8") as log:
        for r in rows:
            out = out_dir / f"{r['id']}.{system.ext}"
            if out.exists():
                continue
            try:
                secs = timed(system, r["text"], out)
            except Exception as e:  # keep going; a failure is a result too
                print(f"FAILED {r['id']}: {e}")
                log.write(json.dumps({"id": r["id"], "error": str(e)}) + "\n")
                continue
            log.write(json.dumps({"id": r["id"], "seconds": round(secs, 3)}) + "\n")
            log.flush()
            print(r["id"], f"{secs:.1f}s")


if __name__ == "__main__":
    main()
