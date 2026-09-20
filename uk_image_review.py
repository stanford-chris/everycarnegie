#!/usr/bin/env python3
"""
uk_image_review.py — a contact sheet for the British photographs the bot is not
confident about.

Stage 3 of `carnegie_images.py` finds a Commons photograph by searching on the
library's name, because Britain's rows have neither a filename nor coordinates.
It splits what it finds in two:

  **confident**  the file's own title says Carnegie. 52 rows, already postable.
  **plausible**  the title names a library in the right place but not Carnegie.
                 153 rows, and they are what this page is for.

⚠️ **The plausible tier is not a smaller version of the confident one, it is a
different risk.** Searching by name finds something for 84% of British rows, and
that is the danger rather than the achievement: Commons will return "The new
Deptford Library", a 1960s branch in the right town, or a brass band standing
outside the right building. A wrong building under a library's name is worse
than no post, and no amount of pattern-matching on a filename can tell a 1905
Carnegie library from its 1968 replacement two streets away.

So they are shown, not shipped. Nothing on this page is postable until a person
looks at it. That is the same rule the rest of the pipeline keeps: unsure means
unpostable.

The page shows each candidate at 320px with the library's name, region and date
beside it, so the judgement is "is this an Edwardian library building, and does
it look like it belongs to that entry" rather than a filename inspection.

Usage:
    python3 uk_image_review.py     # writes data/uk_image_review.html
"""

import csv
import html
import json
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"


def commons_thumb(title, width=480):
    """Thumbnail straight off Commons, no API call: Special:FilePath redirects."""
    f = title[5:] if title.startswith("File:") else title
    return ("https://commons.wikimedia.org/wiki/Special:FilePath/"
            + urllib.parse.quote(f.replace(" ", "_")) + f"?width={width}")


def file_page(title):
    return "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))


CSS = """
:root{color-scheme:light dark;--bg:#faf9f7;--card:#fff;--ink:#1a262b;--muted:#5d6b70;
      --line:#e3e0da;--warn:#a33;--ok:#2c6e49}
@media (prefers-color-scheme:dark){:root{--bg:#14191c;--card:#1c2429;--ink:#e8ddc8;
      --muted:#9aa8ad;--line:#2b353a;--warn:#e08b8b;--ok:#7fbf9a}}
*{box-sizing:border-box}
body{margin:0;padding:36px 22px 90px;background:var(--bg);color:var(--ink);
     font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.wrap{max-width:1180px;margin:0 auto}
h1{font-size:24px;margin:0 0 8px}
h2{font-size:18px;margin:38px 0 10px;padding-top:20px;border-top:1px solid var(--line)}
.sub{color:var(--muted);font-size:14.5px;margin:0 0 8px;max-width:720px}
.box{background:var(--card);border:1px solid var(--line);border-radius:14px;
     padding:16px 18px;margin:0 0 22px;max-width:720px}
.box.warn{border-color:var(--warn)}
.box p{margin:0 0 8px;font-size:14.5px}
.box p:last-child{margin:0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;
      overflow:hidden;display:flex;flex-direction:column}
.card img{width:100%;height:180px;object-fit:cover;display:block;background:var(--line)}
.meta{padding:10px 12px 12px}
.nm{font-weight:600;font-size:14.5px;line-height:1.3}
.rg{color:var(--muted);font-size:12.5px;margin-top:2px}
.fn{color:var(--muted);font-size:11.5px;margin-top:7px;word-break:break-word;
    line-height:1.4}
.fn a{color:inherit}
.note{color:var(--muted);font-size:12px;margin-top:6px;line-height:1.35}
.keep{display:block;margin-top:10px;font-size:12.5px;color:var(--muted);cursor:pointer;
      user-select:none}
.card.on{outline:2px solid var(--ok);outline-offset:-2px}
.card.on .keep{color:var(--ok);font-weight:600}
.bar{position:sticky;bottom:0;background:var(--card);border:1px solid var(--line);
     border-radius:12px;padding:11px 14px;margin:22px 0 10px;display:flex;gap:14px;
     align-items:center;font-size:14px}
.bar button{font:inherit;padding:5px 12px;border-radius:8px;border:1px solid var(--line);
            background:var(--bg);color:var(--ink);cursor:pointer}
textarea{width:100%;height:170px;font:12.5px/1.5 ui-monospace,Menlo,monospace;
         background:var(--card);color:var(--ink);border:1px solid var(--line);
         border-radius:10px;padding:11px}
h2{scroll-margin-top:20px}
"""


def main():
    state = json.loads((DATA / "image_state.json").read_text())
    names = state.get("name", {})

    # ⚠️ A card that has already been judged must not come back. Without this
    # the sheet still offered England's 107 after all 107 had been looked at,
    # which is worse than useless: it reads as work outstanding.
    judged = {}
    ap = DATA / "approved_images.json"
    if ap.exists():
        d = json.loads(ap.read_text())
        judged = {**{k: "approved" for k in d.get("approved", {})},
                  **{k: "rejected" for k in d.get("rejected", {})}}

    with open(DATA / "carnegie_roster.csv") as f:
        rows = [r for r in csv.DictReader(f) if r["kind"] == "public"]
    for i, r in enumerate(rows):
        r["_key"] = f"{i}:{r['name'][:40]}"

    uk = [r for r in rows if r["country"] == "United Kingdom"]
    order = {"England": 0, "Scotland": 1, "Wales": 2, "Northern Ireland": 3}
    uk.sort(key=lambda r: (order.get(r["region"], 9), r["name"]))
    review, confident, nothing, done = [], 0, 0, 0
    for r in uk:
        if f"{r['name']}|{r['city']}|{r['region']}" in judged:
            done += 1
            continue
        got = names.get(r["_key"])
        if got and got.get("title"):
            confident += 1
        elif got and got.get("review"):
            review.append((r, got["review"]))
        else:
            nothing += 1

    doc = ['<meta charset="utf-8">',
           "<title>Carnegie — British photographs to check</title>",
           f"<style>{CSS}</style>", "<div class=wrap>",
           "<h1>British photographs the bot is not confident about</h1>",
           f"<p class=sub>{len(review)} British candidates still to judge, plus a second cohort further "
           f"down that was shipping until today. {confident} British rows matched a file "
           f"whose own title says Carnegie and are already postable; {nothing} found "
           f"nothing at all.</p>",

           "<div class='box warn'><p><b>Nothing here is postable.</b> These are shown, not "
           "shipped, and no post will use one until it is approved.</p>"
           "<p>⚠️ Searching Commons by name finds something for 84% of British rows, and "
           "that is the danger rather than the achievement. It returns “The new Deptford "
           "Library”, a 1960s branch in the right town, or a brass band standing outside "
           "the right building. No filename test can tell a 1905 Carnegie library from its "
           "1968 replacement two streets away, so the machine stops here and a person "
           "starts.</p>"
           "<p>The question for each is simply: <b>does this look like an Edwardian library "
           "building, and does it plausibly belong to that entry?</b> The filename links to "
           "the Commons file page, which carries the photographer, the licence and usually "
           "a description.</p></div>",

           "<h2>The candidates</h2>", "<div class=grid>"]

    seen_region = None
    for i, (r, title) in enumerate(review):
        if r["region"] != seen_region:
            seen_region = r["region"]
            n = sum(1 for x, _ in review if x["region"] == seen_region)
            doc.append(f"</div><h2>{html.escape(seen_region)} · {n}</h2><div class=grid>")
        f = title[5:] if title.startswith("File:") else title
        date = f" · opened {r['date_opened']}" if r["date_opened"] else " · no date"
        # The roster note is the best evidence a person has for judging whether
        # the photograph belongs: "still in use as a library", "now a nursery",
        # "demolished" all decide it faster than the picture does.
        note = (r.get("notes") or "").strip()
        doc.append(
            f"<div class=card data-i='{i}'>"
            f"<a href='{html.escape(file_page(title))}' target=_blank>"
            f"<img loading=lazy src='{html.escape(commons_thumb(title))}' alt=''></a>"
            f"<div class=meta><div class=nm>{html.escape(r['name'])}</div>"
            f"<div class=rg>{html.escape(r['region'])}{html.escape(date)}</div>"
            + (f"<div class=note>{html.escape(note[:150])}</div>" if note else "")
            + f"<div class=fn><a href='{html.escape(file_page(title))}' target=_blank>"
            f"{html.escape(f)}</a></div>"
            f"<label class=keep><input type=checkbox data-name=\"{html.escape(r['name'])}\" "
            f"data-region=\"{html.escape(r['region'])}\" data-file=\"{html.escape(f)}\"> "
            f"keep this one</label></div></div>")

    # The second cohort: rows that DO carry an image in the manifest but are
    # held because it was found by proximity and nothing about the file says
    # Carnegie. Before 19 August 2026 these shipped, and among them were a
    # photograph of a librarian, a hiking trail, and Kitchener's modern central
    # library standing in for the Carnegie one it replaced.
    with open(DATA / "carnegie_images.csv") as f:
        manifest = list(csv.DictReader(f))
    held = [r for r in manifest
            if r["postable"] == "no" and r["image_title"] and r["photographer"]
            and r["country"] not in ("Ireland",)]
    held.sort(key=lambda r: (r["country"], r["region"], r["name"]))
    if held:
        doc.append(f"</div><h2>Held back: found by proximity, no Carnegie evidence · "
                   f"{len(held)}</h2>"
                   "<p class=sub>These were postable until 19 August 2026. Proximity says "
                   "a file was taken near the library; it says nothing about what is in "
                   "the frame.</p><div class=grid>")
        for r in held:
            t = r["image_title"]
            f_ = t[5:] if t.startswith("File:") else t
            doc.append(
                f"<div class=card>"
                f"<a href='{html.escape(file_page(t))}' target=_blank>"
                f"<img loading=lazy src='{html.escape(commons_thumb(t))}' alt=''></a>"
                f"<div class=meta><div class=nm>{html.escape(r['name'])}</div>"
                f"<div class=rg>{html.escape(r['region'])} · {html.escape(r['country'])}</div>"
                f"<div class=fn><a href='{html.escape(file_page(t))}' target=_blank>"
                f"{html.escape(f_)}</a></div>"
                f"<label class=keep><input type=checkbox data-name=\"{html.escape(r['name'])}\" "
                f"data-region=\"{html.escape(r['region'])}\" data-file=\"{html.escape(f_)}\"> "
                f"keep this one</label></div></div>")

    doc += ["</div>",
            "<div class=bar><span id=count>0 kept</span>"
            "<button onclick='dump()'>Show the list</button></div>",
            "<textarea id=out placeholder='The kept ones appear here. Select all, copy, "
            "and paste them back into the chat.'></textarea>",
            """<script>
const boxes = () => [...document.querySelectorAll('.keep input')];
function tally(){ document.getElementById('count').textContent =
  boxes().filter(b=>b.checked).length + ' kept of ' + boxes().length; }
document.addEventListener('change', e => { if (e.target.matches('.keep input')) {
  e.target.closest('.card').classList.toggle('on', e.target.checked); tally(); } });
function dump(){ document.getElementById('out').value =
  boxes().filter(b=>b.checked)
         .map(b=>`${b.dataset.name}\t${b.dataset.region}\t${b.dataset.file}`)
         .join('\n') || '(nothing ticked yet)'; }
tally();
</script>""",
            "</div>"]
    out = DATA / "uk_image_review.html"
    out.write_text("\n".join(doc), encoding="utf-8")
    print(f"wrote {out}")
    print(f"  {len(review)} to check · {confident} already confident · "
          f"{nothing} with nothing · {done} already judged")


if __name__ == "__main__":
    main()
