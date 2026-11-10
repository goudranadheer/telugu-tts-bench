"""Score transcripts and write results/report.md + results/failures.csv.

Usage: python scripts/score.py [--unit akshara] [--testset data/testset.csv]
                               [--transcripts results/transcripts.jsonl]
"""
import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ttsbench.metrics import edit_counts, error_rate  # noqa: E402
from ttsbench.stats import bootstrap_ci, paired_bootstrap  # noqa: E402


def pct(x):
    return f"{100 * x:.1f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", default="akshara", choices=["akshara", "char", "word"])
    ap.add_argument("--testset", default=str(ROOT / "data" / "testset.csv"))
    ap.add_argument("--transcripts", default=str(ROOT / "results" / "transcripts.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "results"))
    args = ap.parse_args()

    with open(args.testset, encoding="utf-8") as f:
        ref = {r["id"]: r for r in csv.DictReader(f)}

    # scores[judge][system][id] = (edits, ref_len)
    scores = defaultdict(lambda: defaultdict(dict))
    failures = []
    with open(args.transcripts, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d["id"] not in ref:
                continue
            r = ref[d["id"]]
            e, n = edit_counts(r["spoken"], d["hyp"], args.unit)
            scores[d["judge"]][d["system"]][d["id"]] = (e, n)
            failures.append({"rate": round(e / max(n, 1), 3), "judge": d["judge"],
                             "system": d["system"], "id": d["id"],
                             "category": r["category"], "ref": r["spoken"], "hyp": d["hyp"]})

    cats = sorted({r["category"] for r in ref.values()})
    md = [f"# Telugu TTS benchmark: {args.unit} error rate (%)", ""]
    for judge, systems in sorted(scores.items()):
        md += [f"## Judge: {judge}", "",
               "| System | n | Overall | 95% CI | " + " | ".join(cats) + " |",
               "|---|---|---|---|" + "---|" * len(cats)]
        for name, by_id in sorted(systems.items()):
            pairs = list(by_id.values())
            lo, hi = bootstrap_ci(pairs)
            cells = []
            for c in cats:
                cp = [v for i, v in by_id.items() if ref[i]["category"] == c]
                cells.append(pct(error_rate(cp)) if cp else "")
            md.append(f"| {name} | {len(pairs)} | {pct(error_rate(pairs))} | "
                      f"{pct(lo)}-{pct(hi)} | " + " | ".join(cells) + " |")
        md.append("")

        # Pairwise significance on shared sentences (TTS systems only).
        names = sorted(n for n in systems if n != "human")
        lines = []
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                ids = sorted(set(systems[a]) & set(systems[b]))
                if len(ids) < 2:
                    continue
                diff, lo, hi, p = paired_bootstrap([systems[a][k] for k in ids],
                                                   [systems[b][k] for k in ids])
                lines.append(f"| {a} vs {b} | {len(ids)} | {100 * diff:+.1f} | "
                             f"{100 * lo:+.1f} to {100 * hi:+.1f} | {p:.3f} |")
        if lines:
            md += ["Paired differences (negative = first system better):", "",
                   "| Pair | n | Diff (pts) | 95% CI | p(first not better) |",
                   "|---|---|---|---|---|", *lines, ""]

    md += ["The `human` row is real FLEURS speech: it is each judge's error floor. "
           "A TTS score is only meaningful relative to that row.", ""]

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.md").write_text("\n".join(md), encoding="utf-8")
    failures.sort(key=lambda d: -d["rate"])
    with open(out / "failures.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(failures[0]) if failures else ["rate"])
        w.writeheader()
        w.writerows(failures)
    print("\n".join(md))


if __name__ == "__main__":
    main()
