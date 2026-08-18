#!/usr/bin/env python3
"""
carnegie_roster.py — build the Carnegie library roster from Wikipedia's lists.

Andrew Carnegie funded 2,509 library buildings between 1883 and 1929: 1,689 in
the United States, 660 in Britain and Ireland, 125 in Canada and 25 across ten
other countries. Wikidata knows only 703 of them, so it cannot be the roster.
Wikipedia's per-state and per-country lists are the comprehensive source, and
this turns them into one CSV.

  discover   The index page links to every list. Titles come from the API, not
             from guessing "List of Carnegie libraries in <state>": the
             non-US ones are grouped by continent, so the pattern does not hold.
  fetch      One page at a time, with a descriptive User-Agent. Wikipedia
             rejects parallel hits from a single client, and the whole harvest
             is under 60 pages, so there is nothing to gain by pushing.
  parse      Each wikitable, keyed on its own headers rather than by column
             position, because the columns differ: US pages have "City or
             town", Canada has "Place" and "Province", and the continental
             pages carry a "Country" column the US ones have no need for.

Two things worth knowing about the output:

  Public and academic are kept apart. Carnegie funded college and university
  libraries as well as public ones, and Wikipedia lists them in a second table
  on the same page. They are distinguishable only by that table's own header
  saying "Institution" where the public one says "Library", so the distinction
  is recorded in the `kind` column rather than silently merged. A bot about
  public libraries should filter on it.

  Coordinates come from the geo microformat, not the address. The Location cell
  holds a street address and, usually, a {{coord}} template that renders as
  <span class="geo">lat; lon</span>. The address is free text of no fixed shape;
  the geo span is machine-written and reliable. Rows without one are kept, with
  empty coordinates, because a Carnegie library with no coordinate is still a
  Carnegie library: dropping it would quietly shrink the roster.

Raw HTML is cached under data/pages/, so re-parsing costs no requests. Delete
that directory to force a refetch.

Usage:
    python3 carnegie_roster.py                # harvest and write the csv
    python3 carnegie_roster.py --refetch      # ignore the cache
    python3 carnegie_roster.py --stdout       # report only, write nothing
"""

import argparse
import copy
import csv
import os
import re
import sys
import time
import urllib.parse

import requests
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
PAGES = os.path.join(DATA, "pages")
OUT = os.path.join(DATA, "carnegie_roster.csv")

INDEX = "List of Carnegie libraries in the United States"
API = "https://en.wikipedia.org/w/api.php"
USER_AGENT = ("everycarnegie-roster/0.1 (https://chris-stanford.com; "
              "stanfordc+claude@mac.com)")
DELAY = 1.0

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})

# Header text -> our column. Compared after lowercasing, stripping footnote
# markers and collapsing whitespace, because the rendered headers carry things
# like "Date granted[1]" and a stray newline inside "City or town".
HEADER_MAP = {
    "library": "name", "library name": "name", "institution": "name",
    "city or town": "city", "place": "city", "town": "city", "city": "city",
    "community": "city", "city or locality": "city",
    "location": "address", "location and street": "address",
    "state": "region", "province": "region", "country": "country",
    "region": "region", "county": "region",
    "date granted": "date_granted", "date of grant": "date_granted",
    "grant amount": "grant", "amount": "grant",
    "date opened": "date_opened", "year opened": "date_opened", "opened": "date_opened",
    "notes": "notes", "status": "notes",
}

FIELDS = ["name", "kind", "city", "region", "country", "date_granted", "grant",
          "date_opened", "address", "lat", "lon", "image_file", "notes",
          "section", "source_page"]

# Everything the index links that is not one of these is a US state, city or
# district, so the country can be inferred rather than left blank.
CONTINENTS = {"Africa", "Europe", "Oceania", "the Caribbean"}
COUNTRIES = {"Canada"}

# Four college libraries sit in a state page's *public* table, so the
# Institution/Library header split does not catch them. The misfiling is
# Wikipedia's, not the parser's, and four is few enough to name.
ACADEMIC_BY_NAME = {
    "Hamline University", "University of Oklahoma", "Seattle University",
    "College View",
}


def log(msg):
    print(msg, flush=True)


def clean(s):
    """Collapse whitespace, and undo the spacing that reading cells with a
    separator introduces: "Bridgetown , ( St. Michael )". Same artefact as the
    one that broke the headers, and it reaches the post text if left."""
    s = re.sub(r"\s+", " ", (s or "")).strip()
    s = re.sub(r"\s+([,.;:)\]])", r"\1", s)
    s = re.sub(r"([(\[])\s+", r"\1", s)
    return s.strip()


def header_text(th):
    r"""Header text with footnotes removed and wrapped words kept apart.

    Both halves matter. These headers wrap with <br>, so reading them without a
    separator fuses "City or<br>town" into "city ortown", which matches nothing.
    Adding the separator then spaces out the footnote markers into "[ 1 ]",
    which a \[\d+\] pattern no longer catches — so the <sup> elements are
    removed outright instead of matched. Getting only one of these right leaves
    the grant amount and the dates silently empty on every US page."""
    th = copy.copy(th)
    for sup in th.find_all("sup"):
        sup.decompose()
    text = re.sub(r"\s+", " ", th.get_text(" ")).strip().lower()
    # Drop parenthesised qualifiers. Canada's "Grant amount (US$)" arrives as
    # "grant amount ( us$ )" once the separator has been applied inside the
    # markup, and matching the literal would only work until the next variant.
    return re.sub(r"\s*\([^)]*\)", "", text).strip()


def fetch(page, refetch=False):
    """Rendered HTML for one page, cached on disk."""
    safe = re.sub(r"[^A-Za-z0-9]+", "_", page)[:120]
    path = os.path.join(PAGES, safe + ".html")
    if os.path.exists(path) and not refetch:
        with open(path, encoding="utf-8") as f:
            return f.read()
    r = SESSION.get(API, params={"action": "parse", "page": page,
                                 "prop": "text", "format": "json"}, timeout=60)
    r.raise_for_status()
    d = r.json()
    if "error" in d:
        log(f"         ! {page}: {d['error'].get('info', 'unknown error')}")
        return ""
    html = d["parse"]["text"]["*"]
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    time.sleep(DELAY)
    return html


def discover(refetch=False):
    """Every list page, taken from the index's own links."""
    r = SESSION.get(API, params={"action": "parse", "page": INDEX,
                                 "prop": "links", "format": "json"}, timeout=60)
    r.raise_for_status()
    titles = sorted({l["*"] for l in r.json()["parse"]["links"]
                     if l.get("ns") == 0 and l["*"].startswith("List of Carnegie libraries in")})
    time.sleep(DELAY)
    return titles


def region_from_title(title):
    return title.replace("List of Carnegie libraries in ", "").strip()


def parse_page(html, title):
    """Every wikitable on the page, as row dicts."""
    soup = BeautifulSoup(html, "lxml")
    out = []
    for table in soup.select("table.wikitable"):
        first_row = table.find("tr")
        headers = [header_text(th) for th in (first_row.find_all("th") if first_row else [])]
        if not headers:
            continue
        # "Institution" marks Carnegie's academic libraries; "Library" the public ones.
        kind = "academic" if any(h == "institution" for h in headers) else "public"
        cols = [HEADER_MAP.get(h, "") for h in headers]
        # Outside the US the lists carry no library-name column: Africa and the
        # Caribbean identify a library by its "Community", Oceania by "Town",
        # Ireland by "Location and street". The town is the name in those lists,
        # so fall back to it rather than discarding the table.
        if "name" not in cols and not ({"city", "address"} & set(cols)):
            continue                                  # not a library table

        section = ""
        prev = table.find_previous(["h2", "h3"])
        if prev:
            section = clean(prev.get_text())

        for tr in table.find_all("tr")[1:]:
            cells = tr.find_all(["td", "th"], recursive=False)
            if len(cells) < 2:
                continue
            row = {f: "" for f in FIELDS}
            row["kind"] = kind
            row["source_page"] = title
            row["region"] = region_from_title(title)
            row["section"] = section

            for i, cell in enumerate(cells):
                key = cols[i] if i < len(cols) else ""
                if not key:
                    continue
                if key == "address":
                    geo = cell.select_one("span.geo")
                    if geo and ";" in geo.get_text():
                        lat, lon = geo.get_text().split(";", 1)
                        row["lat"], row["lon"] = clean(lat), clean(lon)
                    # Strip the coordinate furniture back out of the address.
                    for junk in cell.select("span.geo-inline, span.geo-nondefault, span.plainlinks, sup"):
                        junk.decompose()
                    row["address"] = clean(cell.get_text(" "))
                else:
                    row[key] = clean(cell.get_text(" "))

            img = tr.select_one("img")
            if img and img.get("src"):
                # Strip the query string first: some thumbnails carry campaign
                # tracking parameters that otherwise end up inside the filename.
                src = img["src"].split("?", 1)[0]
                m = re.search(r"/([^/]+?)(?:/\d+px-[^/]+)?$", src)
                if m:
                    row["image_file"] = urllib.parse.unquote(m.group(1))

            if not row["name"]:
                row["name"] = row["city"] or row["address"]
            if row["name"] in ACADEMIC_BY_NAME:
                row["kind"] = "academic"
            # A continental page groups by country under its own headings, so
            # the section is the country when no column supplies one.
            if not row["country"]:
                page_region = region_from_title(title)
                if page_region in CONTINENTS:
                    row["country"] = section or page_region
                elif page_region in COUNTRIES:
                    row["country"] = page_region
                else:
                    row["country"] = "United States"
            # Several lists end with a totals row whose cells are all em dashes.
            if row["name"] and set(row["name"]) <= {"\u2014", "-", " "}:
                continue
            if row["name"]:
                out.append(row)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refetch", action="store_true", help="ignore the page cache")
    ap.add_argument("--stdout", action="store_true", help="report only, write nothing")
    args = ap.parse_args()

    os.makedirs(PAGES, exist_ok=True)
    titles = discover()
    log(f"discovered {len(titles)} list pages from the index")

    rows = []
    for n, t in enumerate(titles, 1):
        html = fetch(t, args.refetch)
        if not html:
            continue
        got = parse_page(html, t)
        rows.extend(got)
        log(f"  {n:>2}/{len(titles)}  {region_from_title(t):<22} {len(got):>4} rows")

    pub = [r for r in rows if r["kind"] == "public"]
    aca = [r for r in rows if r["kind"] == "academic"]
    coords = [r for r in pub if r["lat"]]
    log("")
    log(f"  total rows          {len(rows):>5}")
    log(f"    public libraries  {len(pub):>5}")
    log(f"    academic          {len(aca):>5}")
    log(f"  public with coords  {len(coords):>5}  ({len(coords)/max(len(pub),1)*100:.0f}%)")
    log(f"  public with image   {sum(1 for r in pub if r['image_file']):>5}")
    log("  by country:")
    byc = {}
    for r in pub:
        byc[r["country"]] = byc.get(r["country"], 0) + 1
    for c, n in sorted(byc.items(), key=lambda t: -t[1]):
        log(f"      {c:<24} {n:>5}")

    if args.stdout:
        log("\n--stdout: nothing written")
        return
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    log(f"\nwritten to {OUT}")


if __name__ == "__main__":
    main()
