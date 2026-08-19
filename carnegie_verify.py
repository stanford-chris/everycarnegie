#!/usr/bin/env python3
"""
carnegie_verify.py — does the roster's own evidence hold up?

The roster is Wikipedia's "List of Carnegie libraries in X" pages, so every row
is Wikipedia's claim that a building was Carnegie-funded. That premise is the
bot's whole footing and nothing tested it until 19 August 2026. This does, three
ways, and it is deliberately read-only about the roster: it reports, and it
blanks a link it cannot support, and it changes nothing else.

  1 aggregate   The harvested counts against the documented ones. 1,681 US
                against a documented 1,689, Canada 125 exactly, Indiana 164, the
                figure Indiana is known for.
  2 shape       Duplicate rows, and rows whose name is not a library at all.
  3 corroboration  For every row that links a Wikipedia article — 23% of them —
                fetch that article and look for the word Carnegie. The article
                is a different page written by different editors from the list
                that named the building, so agreement between them is real
                evidence and disagreement is worth seeing.

⚠️ **The redirect trap, and it inverted the result.** Asking the API for an
article by title returns the redirect page itself, not its target, and a
redirect's whole content is one line pointing elsewhere. Without `redirects=1`
this check reported **50** articles that never mention Carnegie. With it, 46 of
those were redirects and the real number is **9**. The first figure was five
times too high and looked entirely plausible.

⚠️ **What this cannot check.** Only 23% of rows link an article. For the other
77% the sole evidence is the list row itself, and no amount of work here
reaches them. A clean run means the checkable quarter checks out.

Usage:
    python3 carnegie_verify.py            # report only
    python3 carnegie_verify.py --apply    # also blank unsupported links in the manifest
"""

import argparse
import collections
import csv
import json
import re
import time
import urllib.parse
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
ROSTER = DATA / "carnegie_roster.csv"
MANIFEST = DATA / "carnegie_images.csv"
REPORT = DATA / "link_check.json"

API = "https://en.wikipedia.org/w/api.php"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "everycarnegie-bot/0.1 "
                                      "(https://chris-stanford.com; stanfordc+claude@mac.com)"})
BATCH, DELAY = 20, 0.25

DOCUMENTED = {"United States": 1689, "Canada": 125}
REGION_KNOWN = {"Indiana": 164}

# Words that would mean the row is not a library building. Tuned once: "Park",
# "Bridge" and "Church" are all common in British and American place names, so
# they are not here — "Crofton Park" and "Sowerby Bridge" are towns with
# libraries, not parks and bridges.
NOT_A_LIBRARY = re.compile(r"\b(lighthouse|gaol|jail|prison|cemetery|"
                           r"bridge over|statue of)\b", re.I)


def article_title(url):
    return urllib.parse.unquote(url.rsplit("/", 1)[1]).replace("_", " ")


def fetch_articles(titles):
    """Wikitext for each title, redirects followed. Keyed by the REQUESTED title.

    ⚠️ The API answers under the resolved title, so the caller cannot look the
    result up by what it asked for unless the redirect map is applied. Skipping
    that is what produced 50 false positives.
    """
    out = {}
    for i in range(0, len(titles), BATCH):
        chunk = titles[i:i + BATCH]
        d = SESSION.get(API, params={
            "action": "query", "prop": "revisions", "rvprop": "content",
            "rvslots": "main", "titles": "|".join(chunk), "redirects": "1",
            "format": "json", "formatversion": "2"}, timeout=90).json()
        q = d.get("query", {})
        resolved = {r["from"]: r["to"] for r in q.get("redirects", []) or []}
        norm = {n["from"]: n["to"] for n in q.get("normalized", []) or []}
        content = {}
        for p in q.get("pages", []):
            try:
                content[p["title"]] = p["revisions"][0]["slots"]["main"]["content"]
            except Exception:
                content[p["title"]] = None
        for t in chunk:
            final = resolved.get(norm.get(t, t), norm.get(t, t))
            out[t] = content.get(final)
        time.sleep(DELAY)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="blank unsupported wikipedia_url values in the manifest")
    args = ap.parse_args()

    rows = [r for r in csv.DictReader(ROSTER.open()) if r["kind"] == "public"]
    print(f"roster: {len(rows)} public libraries\n")

    print("1 · aggregate")
    counts = collections.Counter(r["country"] for r in rows)
    for country, want in DOCUMENTED.items():
        got = counts[country]
        print(f"    {country:<16} {got:>5}  documented {want:>5}   {got - want:+d}")
    for region, want in REGION_KNOWN.items():
        got = sum(1 for r in rows if r["region"] == region)
        print(f"    {region:<16} {got:>5}  known      {want:>5}   {got - want:+d}")
    print(f"    {'United Kingdom':<16} {counts['United Kingdom']:>5}  "
          f"partial by design; Britain and Ireland document ~660 together")

    print("\n2 · shape")
    key = lambda r: (r["name"].strip().lower(), r["region"].strip().lower(), r["country"])
    dups = [k for k, c in collections.Counter(key(r) for r in rows).items() if c > 1]
    print(f"    duplicate rows            {len(dups)}")
    odd = [r for r in rows if NOT_A_LIBRARY.search(r["name"])]
    print(f"    names that are not libraries {len(odd)}")
    for r in odd:
        print(f"        {r['name']} ({r['country']})")

    print("\n3 · corroboration")
    linked = [r for r in rows if r["wikipedia_url"]]
    titles = sorted({article_title(r["wikipedia_url"]) for r in linked})
    print(f"    {len(linked)} rows link {len(titles)} articles "
          f"({100 * len(linked) // len(rows)}% of the roster)")
    text = fetch_articles(titles)
    bad = {t for t, c in text.items() if c and not re.search(r"carnegie", c, re.I)}
    gone = {t for t, c in text.items() if c is None}
    print(f"    articles fetched          {sum(1 for c in text.values() if c)}")
    print(f"    unreachable               {len(gone)}")
    print(f"    never mention Carnegie    {len(bad)}")

    affected = [r for r in linked if article_title(r["wikipedia_url"]) in bad]
    for r in affected:
        print(f"        {r['name'][:26]:<26} {r['region'][:16]:<16} "
              f"-> {article_title(r['wikipedia_url'])}")

    REPORT.write_text(json.dumps(
        {"unsupported_articles": sorted(bad), "unreachable": sorted(gone),
         "rows": [[r["name"], r["city"], r["region"]] for r in affected]}, indent=1))
    print(f"\n    written to {REPORT}")

    if not args.apply:
        print("\n(no --apply: the manifest is untouched)")
        return

    # Blank the link, never the row. A row whose article turns out to be about a
    # park is still a Carnegie library; it is the link that is wrong, and a post
    # whose title links to the wrong article is the fault being fixed here.
    drop = {(r["name"], r["city"], r["region"]) for r in affected}
    with MANIFEST.open() as f:
        man = list(csv.DictReader(f))
        fields = f and csv.DictReader(MANIFEST.open()).fieldnames
    n = 0
    for r in man:
        if (r["name"], r["city"], r["region"]) in drop and r["wikipedia_url"]:
            r["wikipedia_url"] = ""
            n += 1
    with MANIFEST.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(man)
    print(f"\n    blanked {n} unsupported links in {MANIFEST.name}")


if __name__ == "__main__":
    main()
