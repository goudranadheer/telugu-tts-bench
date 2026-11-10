"""Score human verdicts: error rate per system and category, with intervals.

Usage: python scripts/score_listening.py
Reads results/listening/key.csv and results/listening/verdicts.csv,
writes results/listening_report.md. "unsure" and unjudged clips are
reported but excluded from error rates.
"""
import argparse
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ttsbench.listening import mcnemar_exact, wilson  # noqa: E402


def cell(wrong, n):
    if not n:
        return ""
    lo, hi = wilson(wrong, n)
    return f"{100 * wrong / n:.0f}% ({wrong}/{n}; {100 * lo:.0f}-{100 * hi:.0f})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(ROOT / "results" / "listening"))
    ap.add_argument("--out", default=str(ROOT / "results" / "listening_report.md"))
    args = ap.parse_args()
    d = Path(args.dir)

    with open(d / "key.csv", encoding="utf-8") as f:
        key = {r["code"]: r for r in csv.DictReader(f)}
    with open(d / "verdicts.csv", encoding="utf-8") as f:
        verdicts = {r["code"]: r for r in csv.DictReader(f)}

    # judged[system][id] = True if wrong
    judged = defaultdict(dict)
    cat_of, skipped, types = {}, Counter(), defaultdict(Counter)
    for code, k in key.items():
        v = verdicts.get(code, {}).get("verdict", "")
        cat_of[k["id"]] = k["category"]
        if v not in ("correct", "wrong"):
            skipped[k["system"]] += 1
            continue
        judged[k["system"]][k["id"]] = v == "wrong"
        if v == "wrong":
            types[k["system"]][verdicts[code].get("error_type") or "untyped"] += 1

    cats = sorted(set(cat_of.values()))
    md = ["# Human listening check: share of sentences read wrong", "",
          "Each cell: error rate (wrong/judged; 95% Wilson interval).", "",
          "| System | Overall | " + " | ".join(cats) + " | Not judged |",
          "|---|---|" + "---|" * (len(cats) + 1)]
    for s, by_id in sorted(judged.items()):
        cells = []
        for c in cats:
            vals = [w for i, w in by_id.items() if cat_of[i] == c]
            cells.append(cell(sum(vals), len(vals)))
        md.append(f"| {s} | {cell(sum(by_id.values()), len(by_id))} | "
                  + " | ".join(cells) + f" | {skipped[s]} |")

    names = sorted(judged)
    pairs = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ids = set(judged[a]) & set(judged[b])
            a_only = sum(judged[a][k] and not judged[b][k] for k in ids)
            b_only = sum(judged[b][k] and not judged[a][k] for k in ids)
            pairs.append(f"| {a} vs {b} | {len(ids)} | {a_only} | {b_only} | "
                         f"{mcnemar_exact(a_only, b_only):.3f} |")
    if pairs:
        md += ["", "Paired comparison on shared sentences (exact McNemar test):", "",
               "| Pair | n | Only first wrong | Only second wrong | p |",
               "|---|---|---|---|---|", *pairs]

    md += ["", "Error types:", "", "| System | Type | Count |", "|---|---|---|"]
    for s in names:
        md += [f"| {s} | {t} | {n} |" for t, n in types[s].most_common()]
    md += ["", "One listener judged these clips; verdicts are blind to the system "
           "but not independent of the listener.", ""]

    Path(args.out).write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
