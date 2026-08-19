#!/usr/bin/env python3
"""
carnegie_sample_page.py — render sample posts to a local HTML page.

The terminal preview shows the text; this shows the post as a reader meets it,
with the photograph, so the pairing can be judged. Written as a plain local
file rather than anything hosted, because the images are hot-linked from
Wikimedia and a local page in Safari loads them without ceremony.

Usage:
    python3 carnegie_sample_page.py                 # 20 posts
    python3 carnegie_sample_page.py --count 40 --seed 9
    open data/sample_posts.html
"""

import argparse
import csv
import html
import importlib.util
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUT = DATA / "sample_posts.html"

spec = importlib.util.spec_from_file_location("cp", HERE / "carnegie_post_preview.py")
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)

CSS = """
:root { color-scheme: light dark; --bg:#faf9f7; --card:#fff; --ink:#1a262b;
        --muted:#5d6b70; --line:#e3e0da; --accent:#c8890f; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#14191c; --card:#1c2429; --ink:#e8ddc8; --muted:#9aa8ad;
          --line:#2b353a; } }
* { box-sizing:border-box; }
body { margin:0; padding:32px 20px 64px; background:var(--bg); color:var(--ink);
       font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
.wrap { max-width:620px; margin:0 auto; }
h1 { font-size:22px; margin:0 0 4px; }
.sub { color:var(--muted); font-size:14px; margin:0 0 28px; }
.post { background:var(--card); border:1px solid var(--line); border-radius:14px;
        padding:16px 18px 14px; margin:0 0 22px; }
.text { white-space:pre-wrap; margin:0 0 12px; }
img { width:100%; border-radius:10px; display:block; border:1px solid var(--line); }
.alt { color:var(--muted); font-size:13px; margin:10px 0 0; padding-left:10px;
       border-left:2px solid var(--line); }
.meta { color:var(--muted); font-size:12px; margin-top:10px;
        display:flex; gap:14px; flex-wrap:wrap; }
.pending { color:var(--accent); }
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=20)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    with (DATA / "carnegie_roster.csv").open() as f:
        notes = {(r["name"], r["city"], r["region"]): r.get("notes", "")
                 for r in csv.DictReader(f)}
    with (DATA / "carnegie_images.csv").open() as f:
        rows = [r for r in csv.DictReader(f) if r["postable"] == "yes"]
    alt = json.loads((DATA / "alt_text.json").read_text()) if (DATA / "alt_text.json").exists() else {}

    import hashlib

    def lib_id(r):
        return hashlib.sha1(f"{r['name']}|{r['city']}|{r['region']}".encode()).hexdigest()[:12]

    random.Random(args.seed).shuffle(rows)
    described = sum(1 for r in rows if lib_id(r) in alt)

    parts = ['<meta charset="utf-8">', f"<title>Carnegie — sample posts</title>", f"<style>{CSS}</style>", "<div class=wrap>",
             "<h1>Every Carnegie Library — sample posts</h1>",
             f"<p class=sub>{args.count} of {len(rows):,} postable, drawn at random (seed {args.seed}). "
             f"{described:,} of those have a description so far.</p>"]

    for r in rows[:args.count]:
        note = cp.clean_note(notes.get((r["name"], r["city"], r["region"]), ""))
        text = cp.build(r, note)
        entry = alt.get(lib_id(r))
        alt_html = (f"<p class=alt><b>Alt:</b> A.I.-written description: "
                    f"{html.escape(entry['visual'])}</p>" if entry and entry.get("visual")
                    else "<p class='alt pending'><b>Alt:</b> description not generated yet</p>")
        parts.append(
            "<div class=post>"
            f"<p class=text>{html.escape(text)}</p>"
            f"<img loading=lazy src=\"{html.escape(r['image_url'])}\" alt=\"\">"
            f"{alt_html}"
            f"<p class=meta><span>{len(text)} chars</span>"
            f"<span>{html.escape(r['licence'])}</span>"
            f"<span>{html.escape(r['image_source'])}</span></p>"
            "</div>")

    parts.append("</div>")
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"  open {OUT}")


if __name__ == "__main__":
    main()
