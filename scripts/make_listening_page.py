"""Build a blind listening page for human right/wrong verdicts.

Usage: python scripts/make_listening_page.py --systems eleven_v3 eleven_v4 mms
Writes results/listening/index.html (open it in a browser from that folder)
and results/listening/key.csv (clip code -> system, id). Clips are shuffled
and system names are hidden, so the listener cannot favour a system.
Verdicts are kept in the browser and exported with the "Export CSV" button;
save the export as results/listening/verdicts.csv.
"""
import argparse
import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERROR_TYPES = ["skipped", "wrong value", "wrong language", "wrong reading style",
               "garbled", "other"]

PAGE = """<!doctype html><meta charset="utf-8"><title>Listening check</title>
<style>
body{font:16px/1.5 system-ui,sans-serif;max-width:760px;margin:2rem auto;padding:0 1rem}
.clip{border:1px solid #ccc;border-radius:8px;padding:12px;margin:12px 0}
.clip.done{border-color:#2a7;background:#f4fbf7}
.text{font-size:20px;margin:6px 0}.cat{color:#666;font-size:13px}
button{font-size:15px;padding:6px 14px;margin:6px 6px 0 0;border-radius:6px;border:1px solid #888;background:#fff;cursor:pointer}
button.on{background:#222;color:#fff}select,input{font-size:15px;margin-top:6px}
#bar{position:sticky;top:0;background:#fff;padding:8px 0;border-bottom:1px solid #ccc}
</style>
<div id="bar"><b id="count"></b> <button id="export">Export CSV</button></div>
<p>Play each clip. Mark <b>Correct</b> only if everything in the sentence is
spoken, with the right values, in a way a Telugu speaker would accept.
Rules and error types: see data/CATEGORIES.md.</p>
<div id="clips"></div>
<script>
const CLIPS = __CLIPS__, TYPES = __TYPES__, KEY = "listening-" + __SEED__;
let V = {}; try { V = JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) {}
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(V)); } catch (e) {} };
const root = document.getElementById("clips");
function render() {
  root.textContent = "";
  for (const c of CLIPS) {
    const v = V[c.code] || {}, d = document.createElement("div");
    d.className = "clip" + (v.verdict ? " done" : "");
    const cat = document.createElement("div"); cat.className = "cat"; cat.textContent = c.code + " / " + c.category;
    const t = document.createElement("div"); t.className = "text"; t.textContent = c.text;
    const a = document.createElement("audio"); a.controls = true; a.preload = "none"; a.src = c.src;
    d.append(cat, t, a, document.createElement("br"));
    for (const name of ["correct", "wrong", "unsure"]) {
      const b = document.createElement("button"); b.textContent = name;
      if (v.verdict === name) b.className = "on";
      b.onclick = () => { V[c.code] = Object.assign({}, V[c.code], {verdict: name}); save(); render(); };
      d.append(b);
    }
    if (v.verdict === "wrong") {
      const s = document.createElement("select");
      for (const x of [""].concat(TYPES)) { const o = document.createElement("option"); o.value = x; o.textContent = x || "error type"; s.append(o); }
      s.value = v.type || ""; s.onchange = () => { V[c.code].type = s.value; save(); };
      d.append(s);
    }
    const n = document.createElement("input"); n.placeholder = "what was said (optional)"; n.size = 40; n.value = v.note || "";
    n.onchange = () => { V[c.code] = Object.assign({}, V[c.code], {note: n.value}); save(); };
    d.append(document.createElement("br"), n); root.append(d);
  }
  const done = CLIPS.filter(c => (V[c.code] || {}).verdict).length;
  document.getElementById("count").textContent = done + " / " + CLIPS.length + " judged";
}
const q = s => '"' + String(s || "").replace(/"/g, '""') + '"';
document.getElementById("export").onclick = () => {
  const rows = ["code,verdict,error_type,note"].concat(
    CLIPS.map(c => { const v = V[c.code] || {}; return [c.code, v.verdict, v.type, v.note].map(q).join(","); }));
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([rows.join("\\n")], {type: "text/csv"}));
  a.download = "verdicts.csv"; a.click();
};
render();
</script>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--systems", nargs="+", required=True)
    ap.add_argument("--include-fleurs", action="store_true",
                    help="also judge FLEURS sentences (default: hard cases only)")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    with open(ROOT / "data" / "testset.csv", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f)
                if args.include_fleurs or r["category"] != "fleurs"]

    clips = []
    for system in args.systems:
        folder = ROOT / "audio" / system
        for r in rows:
            found = sorted(folder.glob(f"{r['id']}.*"))
            if found:
                clips.append({"system": system, "id": r["id"], "category": r["category"],
                              "text": r["text"],
                              "src": f"../../audio/{system}/{found[0].name}"})
            else:
                print(f"missing audio: {system}/{r['id']}")
    random.Random(args.seed).shuffle(clips)
    for k, c in enumerate(clips):
        c["code"] = f"c{k:04d}"

    out = ROOT / "results" / "listening"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "key.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["code", "system", "id", "category"])
        w.writerows([c["code"], c["system"], c["id"], c["category"]] for c in clips)

    public = [{k: c[k] for k in ("code", "category", "text", "src")} for c in clips]
    blob = json.dumps(public, ensure_ascii=False).replace("</", "<\\/")
    page = (PAGE.replace("__CLIPS__", blob)
                .replace("__TYPES__", json.dumps(ERROR_TYPES))
                .replace("__SEED__", json.dumps(str(args.seed))))
    (out / "index.html").write_text(page, encoding="utf-8")
    print(f"{len(clips)} clips -> {out / 'index.html'}")


if __name__ == "__main__":
    main()
