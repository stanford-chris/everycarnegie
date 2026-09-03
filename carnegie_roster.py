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
    "notes": "notes", "status": "notes", "remarks": "notes",
}

FIELDS = ["name", "kind", "city", "region", "country", "date_granted", "grant",
          "date_opened", "address", "lat", "lon", "image_file", "wikipedia_url",
          "notes", "section", "source_page"]

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
    separator introduces: "Bridgetown , ( St. Michael )". Same artifact as the
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


# ---------------------------------------------------------------- UK bullets
#
# Britain is not in table form. The United Kingdom section of the Europe page is
# bullet lists, so the table parser above walks straight past it and the roster
# has been short by Britain since it was built.
#
# ⚠️ README.md recorded these as unparseable prose — "several libraries crammed
# into each" — and that claim kept anyone from looking again for months. It is
# wrong. Scotland, Wales and Northern Ireland are one library per bullet;
# England is a two-level list with branches nested under their city. It reads as
# run-together prose only if the markup is stripped before parsing, which is
# probably how the claim arose.

UK_SECTIONS = ("England", "Scotland", "Wales", "Northern Ireland")

# Two entries in these lists are not public library buildings, and both say so
# in their own text. "King's College, London" is the Carnegie Collection of
# British Music, on loan to the Maughan Library. "Solon" is "Solon Carnegie
# Library, no building provided. This academic library comprised books on
# ceramics." They are marked academic rather than dropped, which is what the
# roster already does with the four American college libraries filed in public
# tables: the bot filters on `kind`, so marking them keeps them out of the feed
# without quietly shrinking the roster.
UK_ACADEMIC = {"king's college, london", "solon"}

# ⚠️ Bounded, not any four digits. These bullets are prose and carry other
# years: "Bromley 1908, designed by Evelyn Hellicar (1862-1929)" and, worse,
# "Ewart Library, Dumfries, named after William Ewart, MP for Dumfries Burghs
# 1841-1868". An unbounded pattern dated that library to 1841. Carnegie's
# grants run 1883 to 1929 and the buildings finish by 1940, which is also the
# span of the Cardiff gazetteer, so anything outside that is somebody's dates
# and not the building's.
YEAR_RE = re.compile(r"\b(18[89]\d|19[0-3]\d|1940)\b")

MONTHS = {"january", "february", "march", "april", "may", "june", "july",
          "august", "september", "october", "november", "december"}

# Where a bullet stops naming the building and starts reporting on it. Only
# needed for the undated bullets, which have no year to cut at: "Belfast,
# Oldpark Road no longer in use" is a library called Belfast, Oldpark Road.
# Matched on word boundaries, so "Newbuilt" and "Openshaw" are safe.
STATUS_LEAD = re.compile(
    r"\b(?:no longer|still in use|now|closed|demolished|converted|run by|opened|"
    r"built|rebuilt|replaced|destroyed|burnt|bombed|extended|refurbished)\b",
    re.I)


def _bullet_text(li):
    """The bullet's own text: no nested list, no footnote markers."""
    c = copy.copy(li)
    for junk in c.find_all(["ul", "ol", "sup"]):
        junk.decompose()
    return clean(c.get_text(" "))


def _section_lists(soup, heading_id, level=3):
    """Every <ul> between one heading and the next of the same or higher rank.

    MediaWiki wraps headings in <div class="mw-heading mw-heading3">, so the
    walk is over the wrapper's siblings, not the <h3>'s. Reading the level off
    that class is what stops England's list from swallowing Scotland's.
    """
    h = soup.find(id=heading_id)
    if not h:
        return []
    node = h.parent if h.parent and h.parent.name == "div" else h
    out = []
    while True:
        node = node.find_next_sibling()
        if node is None:
            break
        classes = node.get("class") or []
        if "mw-heading" in classes:
            ranks = [c for c in classes if c.startswith("mw-heading") and c[-1].isdigit()]
            if ranks and int(ranks[-1][-1]) <= level:
                break
        if node.name == "ul":
            out.extend(node.find_all("li", recursive=False))
    return out


def _trim_name(head):
    """Cut a name out of the text before the year.

    Taking all of it is wrong twice over: "Inverurie Public Library, August
    1911" yields a library called "Inverurie Public Library, August", and the
    Ewart bullet yields ninety-nine characters of biography. Taking only up to
    the first comma is wrong the other way, losing the town in "Arthurstone
    Library, Dundee".

    So: keep comma-separated pieces while they still look like part of a name,
    and stop at the first one that begins with a lower-case word, which is where
    the sentence starts, or with a month, which is where the date starts.
    """
    parts = head.split(",")
    kept = [parts[0]]
    for chunk in parts[1:]:
        first = (chunk.strip().split(" ") or [""])[0].strip(".")
        if not first or first[:1].islower() or first.lower() in MONTHS:
            break
        kept.append(chunk)
    return ",".join(kept)


def _split_entry(li):
    """(name, year, notes, town) for one bullet.

    The name comes from the leading wikilink where there is one, which is 86% of
    them. That is not a stylistic preference: splitting on the first year
    instead turns "[[Hartlepool]] was built in 1903" into a library called
    "Hartlepool was built in", and "[[Harrogate]] Opened in Victoria Avenue in
    1906" into one called "Harrogate Opened in Victoria Avenue in". The link is
    the subject; the rest of the bullet is a sentence about it.
    """
    text = _bullet_text(li)
    lead = next((e for e in li.contents
                 if getattr(e, "name", None) or clean(str(e))), None)
    name = ""
    if getattr(lead, "name", None) == "a" and not lead.get("href", "").startswith("/wiki/File:"):
        name = clean(lead.get_text(" "))

    m = YEAR_RE.search(text)
    year = m.group(1) if m else ""

    # Where the link names the library and the town follows it, the town is
    # worth keeping: "[[Drury Lane Library]], Wakefield 1905" would otherwise
    # record a library in England and nothing more. Only a short capitalised
    # run qualifies, so the prose in "[[Knutsford]], red brick and terracotta"
    # is not mistaken for a place.
    town = ""
    if name and m:
        between = clean(text[len(name):m.start()]).strip(" ,.;:-\u2013\u2014")
        words = between.split()
        if between and len(words) <= 3 and words[0][:1].isupper() \
                and words[0].lower() not in MONTHS:
            town = between

    if not name:
        # No leading link. Everything before the year, trimmed; and failing a
        # year, the first clause — an undated bullet reads "Sydenham (run by
        # London Borough of Lewisham)." and the parenthesis is not its name.
        head = clean(text[:m.start()]) if m else text
        # An undated bullet runs straight on into its own commentary, with no
        # year to stop at: cut at the parenthesis, the full stop, the dash that
        # introduces a status clause, and failing all three at the status
        # wording itself.
        if not m:
            head = re.split(r"[.(]|\s[-\u2013\u2014]\s", head)[0]
            cut = STATUS_LEAD.search(head)
            if cut and cut.start() > 0:
                head = head[:cut.start()]
        name = _trim_name(clean(head))
    name = clean(name).strip(" ,.;:-\u2013\u2014")

    notes = clean(text[m.end():]) if m else clean(text[len(name):])
    return name, year, notes.strip(" ,.;:-\u2013\u2014"), town


def parse_uk_lists(soup, title):
    """The United Kingdom bullet lists, as roster rows."""
    rows = []
    for section in UK_SECTIONS:
        for li in _section_lists(soup, section.replace(" ", "_")):
            nested = li.find("ul")
            # A bullet with children is a city heading, never a library: none of
            # the six carries a date, and their children all do.
            group = [(clean(_bullet_text(li)).strip(" .,"), sub)
                     for sub in nested.find_all("li", recursive=False)] if nested \
                else [("", li)]

            for city, item in group:
                name, year, notes, town = _split_entry(item)
                if not name:
                    continue
                row = {f: "" for f in FIELDS}
                row.update(kind="academic" if name.lower() in UK_ACADEMIC else "public",
                           name=name, city=city or town, region=section,
                           country="United Kingdom", date_opened=year, notes=notes,
                           section=section, source_page=title)

                # ⚠️ Only from a link that names a library. Most of these point
                # at the TOWN — "[[Aberystwyth]] 1906" is the town article, not
                # its library — and a post whose title links to a town is
                # quietly wrong. Same rule as the table parser's, and the same
                # reason: the Curepipe row.
                a = item.find("a", href=re.compile(r"^/wiki/"))
                if a and "redlink=1" not in a.get("href", "") \
                        and not a["href"].startswith("/wiki/File:") \
                        and "librar" in (a.get("title") or a.get_text()).lower():
                    row["wikipedia_url"] = "https://en.wikipedia.org" + a["href"]

                rows.append(row)
    return rows


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

            # The article about the building, where one exists. Taken from the
            # identifying cell only: the region and image cells link too, to a
            # state article and a File: page, and neither is the subject.
            # Only from a genuine library-name column. Falling back to the
            # city cell looks like it lifts coverage to 91%, but those links go
            # to the TOWN — "Curepipe" the place, not its library — and a post
            # whose title links to a town article is quietly wrong.
            for key in ("name",) if "name" in cols else ():
                cell = cells[cols.index(key)] if cols.index(key) < len(cells) else None
                if not cell:
                    continue
                a = cell.find("a", href=re.compile(r"^/wiki/"))
                # A redlink points at an article that does not exist yet.
                if a and "redlink=1" not in a.get("href", "") \
                        and not a["href"].startswith("/wiki/File:"):
                    row["wikipedia_url"] = "https://en.wikipedia.org" + a["href"]

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

    # Britain is bullets, not tables, so it needs its own pass over the same
    # soup. Keyed on the section headings existing rather than on the page
    # title, so it costs nothing on the 56 pages that have no such section.
    if soup.find(id="United_Kingdom"):
        out.extend(parse_uk_lists(soup, title))
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
