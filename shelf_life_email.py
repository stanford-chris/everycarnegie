#!/usr/bin/env python3
"""
shelf_life_email.py — the letter to the AHRC Shelf-Life project, and a page to
read it on.

⚠️ **The licence question is the whole point of writing, and the first version
of this had it wrong.** The ArcGIS feature layer behind their map carries no
copyrightText and no terms, which looked like an unlicensed dataset. The
project's own site is explicit:

    "Unless otherwise indicated, all material on this site is provided under an
    Attribution Non-Commercial Share-Alike Creative Commons license:
    CC-BY-NC-SA 4.0, and must be credited as © [creator] Cardiff University
    AHRC 'Shelf Life' project [AH/P002587/1]."

So it is licensed, and the ask is not "may we have your data". It is narrower
and more awkward than that:

  **NC** the bot carries no advertising and earns nothing, so the use is
     non-commercial in substance. It posts to Bluesky, which is a commercial
     platform, and NC has always been vague about that. Worth naming rather
     than assuming.
  **SA** ⚠️ the real obstacle, and stronger than "one-way incompatible", which
     is how this file first put it. The roster is built from Wikipedia, which
     is CC BY-SA 4.0. **The two are incompatible in both directions.** BY-SA
     forbids adding restrictions, so a BY-SA work cannot be relicensed
     NC; BY-NC-SA requires adaptations to carry the NC term forward, so it
     cannot be relicensed BY-SA. A merged file would have to be both at once,
     and no licence satisfies both.

     ⚠️ The escape hatch is real but narrow. ShareAlike binds **Adapted
     Material**, not a mere **Collection**: two files kept separate, each under
     its own licence, and read side by side at runtime is a collection. One CSV
     with the rows interleaved is an adaptation. So the fallback works, and it
     is the merge specifically that does not.

Hence the actual request: would they consider releasing the gazetteer *data*
(not the photographs, which are © Oriel Prizeman and not wanted) under CC BY-SA
4.0 or CC BY 4.0, so it can sit in the same file as the Wikipedia-derived rows.
If not, the fallback is a separate file, separately licensed and separately
credited, which is more work and worth avoiding but is not fatal.

Contact details are from their own contact page, read 19 August 2026.

Usage:
    python3 shelf_life_email.py     # writes data/shelf_life_email.{txt,html}
"""

import html
from pathlib import Path

TO = "Shelf-lifeproject@cardiff.ac.uk"
CC = "prizemano@cardiff.ac.uk"
POSTAL = ("Professor Oriel Prizeman\nWelsh School of Architecture\nCardiff University\n"
          "Bute Building\nKing Edward VII Avenue\nCardiff CF10 3NB")
GRANT = "AH/P002587/1"

SUBJECT = "Carnegie Libraries of Britain: licensing the gazetteer data for a public-interest bot"

LETTER = """Dear Professor Prizeman,

I run @everycarnegie.bsky.social, a Bluesky bot that will post information about one Carnegie library at a time with a freely licensed photograph and what is known about the grant. Its roster of 2,151 of the 2,509 buildings comes from parsing Wikipedia’s lists, and Britain is the thin part: 245 entries against a documented 660, most with no date, address or coordinates.

Your gazetteer is the authoritative record and I would like to use it. I’m writing before rather than after the bot starts posting: it opens on 29 August, the anniversary of the first one at Dunfermline.

There is a licensing wrinkle I am happy to work around. Your CC BY-NC-SA 4.0 and my Wikipedia-derived CC BY-SA 4.0 cannot share a file, so I would keep your records separate and under your own licence, credited as © Cardiff University AHRC “Shelf Life” project [{grant}] in the bot’s pinned post and on every British library it posts, with a link to carnegielibrariesofbritain.com. If you would rather it were simpler, would you consider releasing the gazetteer data alone, not the photographs, under CC BY-SA 4.0 or CC BY 4.0?

Either way I would rather have your yes or no than assume one.

One offer back: I have to find a freely licensed photograph for each building, so I would gladly send you the Commons images that I identify for your 493 built entries, with coordinates, as a CSV. Several hundred are likely to be ones your project has not catalogued.

Thank you for making the material available at all: it is the only complete account of these buildings I have found.

With best wishes,

Chris Stanford
chris-stanford.com
""".replace("{grant}", GRANT)

NOTES = [
    ("⚠️ Why write at all, when there is a legal workaround",
     "An earlier draft called this “one licensing problem I cannot solve at my end”. That "
     "was not true. Share-alike binds Adapted Material, not a Collection: two files, each "
     "under its own licence and separately credited, read side by side at run time, is a "
     "collection and needs nobody’s permission. The draft then named that very workaround "
     "four paragraphs later, so it argued against itself — and an AHRC project with "
     "licensing advice would have seen it. The letter now names the workaround in one "
     "sentence and asks whether they would rather it were simpler. ⚠️ It is a question, "
     "not a request to be unblocked: overstating a difficulty to a specialist is the "
     "fastest way to lose them, and it gives away the one thing worth having, which is "
     "their goodwill.\n\n"
     "⚠️ **Cut back hard on 24 August 2026, from 458 words to 262, and the reason "
     "generalises.** The letter had grown three paragraphs of licence law — the BY-SA "
     "and BY-NC-SA mechanics, Adapted Material against Collection, and UK database "
     "right — because it was trying to JUSTIFY why it was writing. None of that "
     "belonged in it. You do not need a legal theory to ask someone whether you may "
     "use their work: “May I use this?” is a complete request, and the reasoning that "
     "establishes why you are entitled to ask is for your own notes, not the reader’s. "
     "Database right is still the strongest reason to ask rather than assume, and it is "
     "recorded in README.md where it belongs. The whole of it is carried in the letter "
     "by one line: “Either way I would rather have your yes or no than assume one.”\n\n"
     "⚠️ The pre-emptive non-commercial defence went with it. Answering an objection "
     "the reader has not made, in a letter she has not read, spends words arguing with "
     "nobody. If she raises it, it is answered better in a reply."),

    ("Superseded: why the merge itself is impossible",
     "Because CC BY-NC-SA cannot be combined with the CC BY-SA the rest of the roster "
     "carries. ⚠️ Since the Wikipedia parser shipped on 19 August the letter is no longer "
     "urgent: 245 British rows are already in. This is now about quality — dates, "
     "coordinates and the 396 buildings Wikipedia does not list at all. Without an answer the extra rows have to "
     "live in a separate file under a separate licence, and every downstream script has to "
     "know which is which."),

    ("Why the ask is for the data and not the photographs",
     "The photographs are all © Oriel Prizeman and reserved. They are also not wanted: the "
     "bot's pictures come from Wikimedia Commons and must be freely licensed to be posted "
     "at all. Saying so in the first paragraph of the request removes the objection they "
     "are most likely to have."),

    ("Why offer the Commons matches back",
     "It is the one thing this project has that theirs does not, it costs nothing to give, "
     "and it makes the exchange mutual rather than extractive. ⚠️ Only offer what can "
     "actually be delivered: the matching runs building by building as the bot posts, so "
     "the full set does not exist yet. The letter says “the photographs I identify”, not "
     "“the photographs I have”."),

    ("What to do if there is no reply",
     "Nothing breaks. The list parser ships regardless and takes the roster past 2,100, "
     "and post 2 of the opening thread already says Britain is not included yet. A month "
     "of silence is an answer, and the fallback is the separate-file arrangement, which "
     "their existing licence already permits for a non-commercial account."),

    ("Why the non-commercial term is met head-on",
     "The account posts to Bluesky, a commercial platform, while carrying no advertising "
     "and earning nothing itself. That is non-commercial in substance, but NC has always "
     "been vague about the distinction, so the letter says so plainly and then moves past "
     "it. ⚠️ The move matters as much as the sentence: raising NC and dismissing it in one "
     "breath stops the reader answering the easy question instead of the real one, which "
     "is share-alike."),
]

CSS = """
:root{color-scheme:light dark;--bg:#faf9f7;--card:#fff;--ink:#1a262b;--muted:#5d6b70;
      --line:#e3e0da;--warn:#a33;--ok:#2c6e49}
@media (prefers-color-scheme:dark){:root{--bg:#14191c;--card:#1c2429;--ink:#e8ddc8;
      --muted:#9aa8ad;--line:#2b353a;--warn:#e08b8b;--ok:#7fbf9a}}
*{box-sizing:border-box}
body{margin:0;padding:38px 22px 100px;background:var(--bg);color:var(--ink);
     font:16.5px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.wrap{max-width:720px;margin:0 auto}
h1{font-size:24px;margin:0 0 8px}
h2{font-size:18px;margin:40px 0 8px;padding-top:20px;border-top:1px solid var(--line)}
.sub{color:var(--muted);font-size:14.5px;margin:0 0 22px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;
      padding:18px 20px;margin:0 0 14px}
.card.warn{border-color:var(--warn)}
.hdr{font-size:14px;color:var(--muted);margin:0 0 4px}
.hdr b{color:var(--ink)}
.letter{white-space:pre-wrap;font-size:16px;line-height:1.62;margin:0}
.note h3{font-size:15.5px;margin:0 0 6px}
.note p{margin:0;color:var(--muted);font-size:14.5px}
.addr{white-space:pre-wrap;font-size:14.5px;color:var(--muted);margin:0}
code{background:var(--line);padding:1px 5px;border-radius:4px;font-size:13.5px}
"""


def main():
    here = Path(__file__).resolve().parent
    (here / "data").mkdir(exist_ok=True)

    plain = (f"To: {TO}\nCc: {CC}\nSubject: {SUBJECT}\n\n{LETTER}")
    (here / "data" / "shelf_life_email.txt").write_text(plain, encoding="utf-8")

    doc = ['<meta charset="utf-8">',
           "<title>Carnegie — letter to Shelf-Life</title>", f"<style>{CSS}</style>",
           "<div class=wrap>",
           "<h1>Letter to the AHRC Shelf-Life project</h1>",
           "<p class=sub>Drafted 19 August 2026. Nothing is sent: this is a draft to read "
           "and change. Contact details are from the project’s own contact page.</p>",

           "<div class='card warn'><h3 style='margin:0 0 8px;font-size:16px'>"
           "⚠️ The licence position, corrected</h3>"
           "<p style='margin:0 0 8px;font-size:14.5px;color:var(--muted)'>The ArcGIS layer "
           "behind their map carries no copyright text, which read as an unlicensed "
           "dataset. The project’s site is explicit: everything is "
           "<b>CC BY-NC-SA 4.0</b>, credited as "
           f"<code>© [creator] Cardiff University AHRC “Shelf Life” project [{GRANT}]</code>.</p>"
           "<p style='margin:0;font-size:14.5px;color:var(--muted)'>That makes the ask "
           "narrower and sharper. <b>CC BY-SA and CC BY-NC-SA are one-way incompatible</b>, "
           "so their rows cannot be merged into a roster built from Wikipedia without "
           "dragging 1,910 CC BY-SA rows into a non-commercial licence they cannot take. "
           "The letter therefore asks for the data alone, under CC BY-SA or CC BY, and "
           "offers a fallback.</p></div>",

           "<h2>The letter</h2>",
           "<div class=card>",
           f"<p class=hdr><b>To</b> {TO}</p>",
           f"<p class=hdr><b>Cc</b> {CC}</p>",
           f"<p class=hdr style='margin-bottom:14px'><b>Subject</b> {html.escape(SUBJECT)}</p>",
           f"<p class=letter>{html.escape(LETTER)}</p>",
           "</div>",

           "<h2>Postal address, if it is ever wanted</h2>",
           f"<div class=card><p class=addr>{html.escape(POSTAL)}</p></div>",

           "<h2>Why it is written this way</h2>"]

    for title, why in NOTES:
        doc.append(f"<div class='card note'><h3>{title}</h3><p>{why}</p></div>")

    doc.append("</div>")
    out = here / "data" / "shelf_life_email.html"
    out.write_text("\n".join(doc), encoding="utf-8")
    print(f"wrote {out}")
    print(f"wrote {here / 'data' / 'shelf_life_email.txt'}")
    print(f"  {len(LETTER.split())} words")


if __name__ == "__main__":
    main()
