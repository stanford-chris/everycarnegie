#!/usr/bin/env python3
"""
britain_options.py — how to get Britain's Carnegie libraries into the roster.

The roster holds 1,910 of 2,509 and the shortfall is almost entirely British.
README.md records four sources tried and rejected. This is the re-examination,
done 19 August 2026, and it changes two of those verdicts.

⚠️ **README.md is wrong about the Wikipedia lists, and the error matters**,
because it is the reason nobody looked again. It says England's entries are
"prose bullet lists" with "several libraries crammed into each" and no useful
structure. Checked against the live wikitext today, Scotland, Wales and Northern
Ireland are **one library per bullet** with a name, a year and usually a
wikilink, and England is a **two-level list**: `* [[City]]` with `** [[Branch]]
year, notes` beneath it. That is a nested list, not crammed prose. It reads as
run-together prose only if the markup is stripped before it is parsed, which is
the likely origin of the claim.

⚠️ **A source nobody had found does exist**, and it is better than anything in
the roster today: the AHRC-funded Carnegie Libraries of Britain project at
Cardiff serves its whole gazetteer from a public ArcGIS FeatureServer. 621
records with coordinates, dates, architects and current status.

⚠️ **It is licensed CC BY-NC-SA 4.0, and this file said otherwise for a few
hours.** The feature layer's own metadata carries no copyrightText and no terms,
which read as unlicensed; the project's site is explicit that everything on it
is CC BY-NC-SA 4.0, credited as © [creator] Cardiff University AHRC "Shelf Life"
project [AH/P002587/1]. Checking the endpoint is not checking the licence.

That makes the problem narrower and sharper than "ask permission". **CC BY-SA
and CC BY-NC-SA are one-way incompatible**, so these rows cannot go into a
roster built from Wikipedia without dragging 1,910 CC BY-SA rows into a
non-commercial licence they are not free to take. See `shelf_life_email.py`.

Nothing here harvests anything. It counts what each source would yield and
writes the page.

Usage:
    python3 britain_options.py     # writes data/britain_options.html
"""

from pathlib import Path

# ------------------------------------------------------- measured 19 Aug 2026

WIKIPEDIA = {
    "England": dict(top=103, top_dated=92, nested=66),
    "Scotland": dict(top=43, top_dated=30, nested=0),
    "Wales": dict(top=32, top_dated=32, nested=0),
    "Northern Ireland": dict(top=9, top_dated=5, nested=0),
}
WIKI_TOTAL = sum(v["top_dated"] + v["nested"] for v in WIKIPEDIA.values())   # 225

GRANT = "AH/P002587/1"

CLB_LAYER = ("https://services6.arcgis.com/RZ8g7e9Htqe5KBoA/arcgis/rest/services/"
             "CLofBritain_v26012021/FeatureServer/0")
CLB = dict(
    records=621, never_built=128, built=493, standing=451, with_coords=492,
    fields="library name, build or grant-spent date, architect, type, status, "
           "re-purposed use, image URL, image credit, latitude and longitude",
    span="1883 to 1940",
)
CLB_STATUS = [("open library", 221), ("re-purposed", 118),
              ("village hall and reading room", 52), ("demolished", 42),
              ("closed library", 29), ("village hall", 11), ("bombed", 5),
              ("coming back", 4), ("burnt down", 4), ("village hall and institute", 4),
              ("institute", 1), ("blew down", 1), ("books only grant", 1)]

OPTIONS = [
    ("1", "Parse Wikipedia's Europe list properly", "~225 buildings",
     "CC BY-SA, identical to the rest of the roster", "recommended, do first",
     "The entries are structured, not prose: Scotland, Wales and Northern Ireland run one "
     "library per bullet with a year and usually a wikilink, and England nests branches "
     "under their city. It needs a second parser, because the existing one reads tables "
     "and these are lists, but it is a parser and not a research project. Costs nothing, "
     "asks nobody, and every row arrives under the licence the roster already uses. It "
     "gets a third of the way and it can ship this week."),

    ("2", "Ask Carnegie Libraries of Britain for their gazetteer", "621 records, 493 built",
     "CC BY-NC-SA 4.0", "recommended, in parallel",
     "The AHRC 'Shelf-Life' project at Cardiff, led by Oriel Prizeman, built its map from "
     "research lists supplied by the Carnegie UK Trust combined with the statutory lists. "
     "It is the authoritative British roster and it is better than the American data the "
     "bot already posts: 100% dates, 100% status, 492 of 493 built entries with "
     "coordinates, architects on 65%. ⚠️ **It is CC BY-NC-SA 4.0**, which is one-way "
     "incompatible with the CC BY-SA the roster already carries: merging the two would "
     "drag 1,910 Wikipedia-derived rows into a non-commercial licence they cannot take. "
     "So the ask is not for permission but for the gazetteer data alone, without the "
     "photographs, under CC BY-SA or CC BY. Letter drafted in shelf_life_email.py."),

    ("3", "Wikipedia as the spine, their data as enrichment", "225 rows, better filled",
     "mixed; needs 2's permission", "fallback if 2 is refused in part",
     "Keeps every row under CC BY-SA and uses the gazetteer only to fill coordinates and "
     "dates. Weaker than it sounds: the value in their data is the 396 buildings "
     "Wikipedia does not list at all, and this option is the one that does not take them."),

    ("4", "Historic England, Historic Environment Scotland and Cadw", "partial, listed only",
     "Open Government Licence", "verification, not a roster",
     "Statutory listing records carry addresses, coordinates, grades and full descriptions "
     "that frequently name Carnegie, and they are properly open. But only listed buildings "
     "appear, so it can confirm and enrich rows it will never complete. ⚠️ Historic "
     "England's website returned 403 to a scripted request today; the open data downloads "
     "are the route, not the search page."),

    ("5", "Columbia University's digitised Carnegie Corporation records", "primary source",
     "per-item, varies", "not for bulk",
     "The grant correspondence itself, item by item, including British towns. The right "
     "place to settle a disputed date or grant figure, and the wrong tool for building a "
     "roster of 660."),

    ("6", "Miller, 'Carnegie Grants for Library Buildings 1890–1917' (1943)", "authoritative",
     "print", "reference only",
     "The published list of every building erected with Carnegie or Carnegie Corporation "
     "money. It is what the modern projects were themselves built from. Not digital, so "
     "it is a check on a finished roster rather than a source for one."),

    ("7", "Wikidata", "66 UK items, mostly not libraries", "CC0", "rejected, re-confirmed",
     "Re-run today with a fresh query. 66 UK items carry 'Carnegie' in their label and "
     "they are largely hockey clubs, a theatre, a museum and the Trust itself. ⚠️ The "
     "reason is structural and kills every name-based approach: **British Carnegie "
     "libraries are named after their town, not after Carnegie.** Renfrew's is Renfrew "
     "Library."),

    ("8", "Commons subcategories", "~79 buildings", "CC BY-SA", "rejected, unchanged",
     "Tried before. Photographs of the famous ones, no gazetteer behind them."),

    ("9", "Name-matching everylibrary's UK corpus", "5", "n/a", "rejected, unchanged",
     "Fails for the same structural reason as Wikidata. Matching on coordinates against "
     "option 2's data would work, and that is really a use of option 2."),

    ("10", "Leave it, and keep the disclosure", "0", "n/a", "rejected",
     "Post 2 of the opening thread now says 'Britain's 660 are not included yet', so the "
     "account is honest either way. Rejected because option 1 is nearly free and the "
     "account is called 'every'."),
]

CSS = """
:root{color-scheme:light dark;--bg:#faf9f7;--card:#fff;--ink:#1a262b;--muted:#5d6b70;
      --line:#e3e0da;--warn:#a33;--ok:#2c6e49;--flag:#8a6d1f}
@media (prefers-color-scheme:dark){:root{--bg:#14191c;--card:#1c2429;--ink:#e8ddc8;
      --muted:#9aa8ad;--line:#2b353a;--warn:#e08b8b;--ok:#7fbf9a;--flag:#d9bd6a}}
*{box-sizing:border-box}
body{margin:0;padding:38px 22px 100px;background:var(--bg);color:var(--ink);
     font:16.5px/1.58 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.wrap{max-width:820px;margin:0 auto}
h1{font-size:25px;margin:0 0 8px}
h2{font-size:19px;margin:44px 0 6px;padding-top:22px;border-top:1px solid var(--line)}
.sub{color:var(--muted);font-size:14.5px;margin:0 0 6px}
.lede{margin:0 0 22px;font-size:15.5px}
.box{background:var(--card);border:1px solid var(--line);border-radius:14px;
     padding:16px 18px;margin:0 0 13px}
.box.warn{border-color:var(--warn)}
.box h3{font-size:16px;margin:0 0 8px}
.box p{margin:0 0 8px;font-size:14.5px}
.box p:last-child{margin:0}
table{border-collapse:collapse;width:100%;margin-top:14px;font-size:14px}
th,td{text-align:left;vertical-align:top;padding:9px 10px;border-bottom:1px solid var(--line)}
th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.pill{font-size:11.5px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;
      padding:2px 8px;border-radius:99px;white-space:nowrap;display:inline-block}
.rec{background:var(--ok);color:#fff}
.rej{background:var(--line);color:var(--muted)}
.mid{background:var(--flag);color:#fff}
.opt{background:var(--card);border:1px solid var(--line);border-radius:14px;
     padding:15px 17px;margin:0 0 11px}
.opt h3{font-size:15.5px;margin:0 0 7px}
.opt .meta{color:var(--muted);font-size:13px;margin:0 0 8px}
.opt p{margin:0;color:var(--muted);font-size:14.5px}
code{background:var(--line);padding:1px 5px;border-radius:4px;font-size:13px}
.bar{display:flex;height:26px;border-radius:6px;overflow:hidden;margin:14px 0 6px;
     border:1px solid var(--line)}
.bar div{display:flex;align-items:center;justify-content:center;font-size:11.5px;
         font-weight:700;color:#fff;white-space:nowrap;overflow:hidden}
.key{color:var(--muted);font-size:13px}
"""


def pill(v):
    if v.startswith("recommended"):
        return "rec"
    if v.startswith("rejected"):
        return "rej"
    return "mid"


def main():
    have, wiki, clb_extra = 1910, WIKI_TOTAL, CLB["built"] - WIKI_TOTAL
    total = 2509

    doc = [f'<meta charset="utf-8">'
           f"<title>Carnegie — getting Britain</title><style>{CSS}</style>",
           "<div class=wrap>",
           "<h1>How to get Britain’s Carnegie libraries</h1>",
           "<p class=sub>Re-examined 19 August 2026. Every source, including the ones "
           "already rejected and the ones rejected again.</p>",

           "<p class=lede>The roster holds <b>1,910 of 2,509</b> and the shortfall is "
           "almost entirely British. Two things changed today: one of README.md’s four "
           "rejections turns out to rest on a mistaken reading of the source, and a "
           "gazetteer nobody had found is sitting on a public endpoint.</p>",

           "<div class='box warn'><h3>⚠️ README.md is wrong about the Wikipedia lists</h3>"
           "<p>It records England as “prose bullet lists” with “several libraries crammed "
           "into each” and no usable structure, and that is why nobody looked again. "
           "Checked against the live wikitext today:</p>"
           "<p><b>Scotland, Wales and Northern Ireland are one library per bullet</b>, with "
           "a name, a year and usually a wikilink: "
           "<code>* [[Airdrie Public Library]] 1894 and 1925</code>. "
           "<b>England is a two-level list</b>, branches nested under their city: "
           "<code>* [[Coventry]]</code> then <code>** [[Earlsdon]] Library 1913.</code></p>"
           "<p>That is a nested list, not crammed prose. It reads as run-together prose "
           "only if the markup is stripped before parsing, which is the likely origin of "
           "the claim. ⚠️ The four-source table in README.md needs correcting either way, "
           "because it is currently an argument for not trying.</p></div>",

           "<h2>1 · What each source is actually worth</h2>",
           "<p class=sub>Counted, not estimated. Wikipedia figures are from the live "
           "wikitext; the gazetteer figures are from its own feature layer.</p>"]

    doc.append("<table><tr><th>Wikipedia’s Europe list</th><th class=num>Top-level, "
               "dated</th><th class=num>Nested branches</th><th class=num>Usable</th></tr>")
    for name, v in WIKIPEDIA.items():
        doc.append(f"<tr><td>{name}</td><td class=num>{v['top_dated']} of {v['top']}</td>"
                   f"<td class=num>{v['nested']}</td>"
                   f"<td class=num><b>{v['top_dated'] + v['nested']}</b></td></tr>")
    doc.append(f"<tr><td><b>Total</b></td><td class=num></td><td class=num></td>"
               f"<td class=num><b>{WIKI_TOTAL}</b></td></tr></table>")

    doc += ["<h2>2 · The source nobody had found</h2>",
            "<div class=box>"
            "<h3>Carnegie Libraries of Britain, the AHRC “Shelf-Life” project</h3>"
            "<p>Cardiff University, led by Oriel Prizeman. Its interactive map is an "
            "ArcGIS web app, and the app’s layer is a public FeatureServer:</p>"
            f"<p><code>{CLB_LAYER}</code></p>"
            f"<p><b>{CLB['records']} records</b>, {CLB['span']}, carrying {CLB['fields']}. "
            f"Built from research lists supplied by the Carnegie UK Trust combined with the "
            f"statutory lists, which is to say it is the authoritative British roster.</p>"
            f"<p>Of the {CLB['records']}: <b>{CLB['never_built']} were never built</b> — "
            f"grants offered and refused, or lapsed — leaving <b>{CLB['built']} buildings</b>, "
            f"of which <b>{CLB['standing']} are still standing</b> in some form and "
            f"{CLB['with_coords']} of {CLB['built']} carry coordinates.</p>"
            "<p>⚠️ It is better than the data the bot already posts. The American rows have "
            "coordinates on 31%; these have them on 99%.</p></div>",

            "<div class='box warn'><h3>⚠️ It is CC BY-NC-SA 4.0, and that decides "
            "how it can be used</h3>"
            "<p>The feature layer’s own metadata carries no copyright text and no terms, "
            "which reads as an unlicensed dataset. It is not. The project’s site is "
            "explicit: everything on it is <b>CC BY-NC-SA 4.0</b>, to be credited as "
            f"<code>© [creator] Cardiff University AHRC “Shelf Life” project [{GRANT}]</code>. "
            "⚠️ Checking the endpoint is not checking the licence, and this page said "
            "“no licence stated” for a few hours on the strength of the endpoint alone.</p>"
            "<p><b>CC BY-SA and CC BY-NC-SA are one-way incompatible.</b> The roster is "
            "derived from Wikipedia and is CC BY-SA 4.0, so merging these rows into it "
            "would drag 1,910 rows into a non-commercial licence they are not free to "
            "take. The ask is therefore not “may we use this” — the licence already "
            "answers that for a non-commercial account — but whether the gazetteer data "
            "alone could be released under CC BY-SA or CC BY. Drafted in "
            "<code>shelf_life_email.py</code>.</p>"
            "<p>Separately, <b>every photograph is “© Oriel Prizeman”</b> and reserved. "
            "That costs nothing: the bot’s pictures come from Wikimedia Commons and have "
            "to be freely licensed to be posted at all. What is wanted is the gazetteer — "
            "names, dates, architects, status, coordinates.</p></div>",

            "<h2>3 · What their status field records</h2>",
            "<p class=sub>Of the 493 that were built. It is a richer vocabulary than the "
            "roster’s own, and some of it is the account’s best material.</p><table>"
            "<tr><th>Status</th><th class=num>Count</th></tr>"]
    for k, v in CLB_STATUS:
        doc.append(f"<tr><td>{k}</td><td class=num>{v}</td></tr>")
    doc.append("</table><p class=sub style='margin-top:10px'>“Bombed”, “burnt down”, "
               "“blew down”, “books only grant”, “coming back”. Also, outside this table, "
               "the 85 towns recorded as <b>grant offered and refused</b>: the ones that "
               "read the terms and said no.</p>")

    doc += ["<h2>4 · Where each route gets to</h2>",
            "<div class=bar>"
            f"<div style='flex:{have};background:#2c6e49'>1,910 in the roster now</div>"
            f"<div style='flex:{wiki};background:#8a6d1f'>+{wiki} Wikipedia</div>"
            f"<div style='flex:{clb_extra};background:#a33'>+{clb_extra} only in the gazetteer</div>"
            f"<div style='flex:{total - have - wiki - clb_extra};background:#8895a0'>still short</div>"
            "</div>",
            f"<p class=key>Option 1 alone reaches about {have + wiki:,} of {total:,}. "
            f"Options 1 and 2 together reach about {have + CLB['built']:,}, and the "
            f"remainder is Ireland’s 56, already harvested and held back, plus the "
            f"difference between counting buildings and counting grants.</p>",

            "<h2>5 · Every option, including the ones already rejected</h2>"]
    for num, title, yield_, lic, verdict, why in OPTIONS:
        doc.append(f"<div class=opt><h3>{num}. {title} "
                   f"<span class='pill {pill(verdict)}'>{verdict}</span></h3>"
                   f"<p class=meta>Yield: <b>{yield_}</b> · Licence: {lic}</p>"
                   f"<p>{why}</p></div>")

    doc += ["<h2>6 · What I would do</h2>",
            "<div class=box><p><b>Both, starting today, in this order.</b></p>"
            "<p><b>Write the list parser</b> (option 1). It is a day's work at most, every "
            "row arrives under the licence the roster already uses, it needs nobody's "
            "permission, and it corrects a claim in README.md that is currently telling "
            "future sessions not to bother. It takes the account past 2,100.</p>"
            "<p><b>Write to the Shelf-Life project</b> (option 2) in parallel, because the "
            "reply is the long pole and the ask is small: their gazetteer without their "
            "photographs, credited by name on the pinned post. If they say yes, Britain is "
            "done properly and the roster gains 396 buildings Wikipedia does not list. If "
            "they say no, option 1 has already shipped.</p>"
            "<p>⚠️ Nothing has been harvested. The counts on this page come from reading "
            "the endpoints, which is what the map itself does when anyone opens it.</p>"
            "</div>", "</div>"]

    out = Path(__file__).resolve().parent / "data" / "britain_options.html"
    out.write_text("\n".join(doc), encoding="utf-8")
    print(f"wrote {out}")
    print(f"  Wikipedia parse would yield ~{WIKI_TOTAL}")
    print(f"  gazetteer holds {CLB['records']} records, {CLB['built']} built, "
          f"{CLB['standing']} standing")


if __name__ == "__main__":
    main()
