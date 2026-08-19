#!/usr/bin/env python3
"""
carnegie_images.py — find a freely-licensed photograph for each Carnegie library.

Two stages, and deliberately not the three that everylibrary uses:

  1. roster image   The Wikipedia list pages already illustrate most entries, so
                    the filename is in the roster and only its attribution needs
                    resolving. This is the cheap majority and needs no
                    coordinates, which matters because only 31% of the roster
                    has any.
  2. geosearch      A Commons file within RADIUS_M whose title mentions a
                    library or Carnegie. Only possible for rows that do have
                    coordinates, and only run where stage 1 found nothing.

⚠️ **Neither stage can see the British rows, and the run on 19 August 2026
proved it: 245 rows, 0 images, 0 postable.** Stage 1 needs a filename from the
roster and stage 2 needs coordinates; Britain comes from bullet lists and has
neither. Adding Britain to the roster therefore did not add it to the feed, and
re-running this script will not change that however many times it is run.

⚠️ **The paragraph that used to sit here is now stale, and it was load-bearing.**
It read: "There is no Geograph stage. Geograph covers Britain and Ireland, and
this roster is overwhelmingly American: it supplied a third of everylibrary's
coverage and would supply almost none here." That was true when the roster held
no British rows. It holds 245 now, and Geograph is the source that covers
exactly them. The rejection needs re-deciding rather than inheriting.

Every row that ends up postable carries photographer, licence and a credit URL,
because these are CC BY-SA and attribution is a condition of use. A row with an
image but no resolvable photographer is marked unpostable rather than shipped.

Resumable: resolved metadata is cached in data/image_state.json.

Usage:
    python3 carnegie_images.py             # both stages
    python3 carnegie_images.py --stage 1
    python3 carnegie_images.py --reset
"""

import argparse
import json
import csv
import os
import re
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
ROSTER = os.path.join(DATA, "carnegie_roster.csv")
STATE = os.path.join(DATA, "image_state.json")
OUT = os.path.join(DATA, "carnegie_images.csv")

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = ("everycarnegie-bot/0.1 (https://chris-stanford.com; "
              "stanfordc+claude@mac.com)")
RADIUS_M = 250

# ⚠️ Held back, not missing. Ireland's 56 rows come from the Europe page, whose
# table has no library-name column: the identity is the "Location and street"
# cell, so the names are streets rather than libraries ("Anglesea Street",
# "Charleville Mall, North Strand"), two places repeat a component, the notes
# are mostly bare footnote markers, and one entry is Kish Bank lighthouse, which
# is not a library. That is a different standard of evidence from the American
# tables, which carry a Library column, a grant and a date. 18 postable rows,
# 1.4% of the corpus. Check them by hand against Irish sources and remove this.
HELD_COUNTRIES = {"Ireland"}
THUMB_WIDTH = 1600
BATCH = 50
DELAY = 0.15

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})

# ⚠️ date_opened is carried because Britain has no grant and no date granted:
# its bullet lists give the year the building opened and nothing else. Without
# it in the manifest the composer sees no date at all and a British post is a
# name and a sentence fragment. Added 19 August 2026.
FIELDS = ["name", "kind", "city", "region", "country", "date_granted", "grant",
          "date_opened",
          "address", "lat", "lon", "wikipedia_url", "image_source", "image_title",
          "image_url", "photographer", "licence", "licence_url", "credit_page",
          "postable"]


def log(m):
    print(m, flush=True)


def get(params, retries=3):
    for a in range(retries):
        try:
            r = SESSION.get(COMMONS_API, params=params, timeout=60)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 503):
                time.sleep(2 * (a + 1))
                continue
            return None
        except (requests.RequestException, ValueError):
            time.sleep(1.5 * (a + 1))
    return None


def load_state():
    if os.path.exists(STATE):
        with open(STATE) as f:
            return json.load(f)
    return {"imageinfo": {}, "geo": {}}


def save_state(s):
    tmp = STATE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(s, f)
    os.replace(tmp, STATE)


def strip_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


def resolve(titles, state):
    todo = [t for t in titles if t not in state["imageinfo"]]
    log(f"resolve  {len(titles)} files, {len(todo)} to fetch")
    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        d = get({"action": "query", "format": "json", "prop": "imageinfo",
                 "iiprop": "url|extmetadata|size|user", "iiurlwidth": THUMB_WIDTH,
                 "titles": "|".join(chunk)})
        if d is None:
            log(f"         chunk at {i} failed")
            continue
        norm = {n["to"]: n["from"] for n in d.get("query", {}).get("normalized", [])}
        for page in d.get("query", {}).get("pages", {}).values():
            title = norm.get(page.get("title"), page.get("title"))
            if "imageinfo" not in page:
                state["imageinfo"][title] = None      # missing or local-only
                continue
            ii = page["imageinfo"][0]
            ex = ii.get("extmetadata", {})
            state["imageinfo"][title] = {
                "url": ii.get("thumburl") or ii.get("url"),
                "page": ii.get("descriptionurl", ""),
                "artist": strip_html(ex.get("Artist", {}).get("value", "")) or ii.get("user", ""),
                "licence": strip_html(ex.get("LicenseShortName", {}).get("value", "")),
                "licence_url": ex.get("LicenseUrl", {}).get("value", ""),
            }
        for t in chunk:
            state["imageinfo"].setdefault(t, None)
        save_state(state)
        log(f"         {min(i + BATCH, len(todo)):>5}/{len(todo)}")
        time.sleep(DELAY)


def geosearch(rows, state):
    pending = [r for r in rows
               if r["lat"].strip() and not r["image_file"].strip()
               and r["_key"] not in state["geo"]]
    log(f"stage 2  geosearch: {len(pending)} libraries with coordinates and no picture")
    for n, r in enumerate(pending, 1):
        d = get({"action": "query", "format": "json", "list": "geosearch",
                 "gsnamespace": 6, "gscoord": f"{r['lat']}|{r['lon']}",
                 "gsradius": RADIUS_M, "gslimit": 50})
        hits = (d or {}).get("query", {}).get("geosearch", []) or []
        cand = [h for h in hits
                if "librar" in h["title"].lower() or "carnegie" in h["title"].lower()]
        if cand:
            best = min(cand, key=lambda h: h.get("dist", RADIUS_M))
            state["geo"][r["_key"]] = {"title": best["title"],
                                       "dist": round(best.get("dist", 0))}
        else:
            state["geo"][r["_key"]] = None
        if n % 50 == 0 or n == len(pending):
            save_state(state)
            log(f"         {n:>5}/{len(pending)}  matched {sum(1 for v in state['geo'].values() if v)}")
        time.sleep(DELAY)


# ⚠️ Stage 3 exists because stages 1 and 2 are blind to Britain, proved by the
# run of 19 August 2026: 245 rows, 0 images. There is no filename to follow and
# no coordinate to search around, so the only handle left is the library's name.
#
# Searching by name finds something for 84% of them and **that is the danger,
# not the achievement**. Commons will happily return "The new Deptford Library",
# a 1960s branch in the right town, or a brass band standing outside. A wrong
# building under a library's name is worse than no post at all.
#
# So the bar is the word Carnegie in the file's own title, which takes 21% and
# leaves the rest alone. Everything that merely mentions a library in the right
# place is written to a review file for a person to look at, and is never
# promoted automatically. That follows the rule the rest of this script already
# keeps: unsure means unpostable, not shipped.

# Parts of a building, not the building. A title naming one of these is a
# detail shot even when it is the right library.
NAME_DETAIL = re.compile(
    r"\b(memorial|plaque|ceiling|interior|inside|relief|balcony|stained|window|"
    r"door(?:way)?|mosaic|bust|statue|sign|shelves|bookcase|staircase|mural|"
    r"clock|foundation stone|chart|map|portrait|painting)\b", re.I)
NAME_LIBRARYISH = re.compile(r"\b(?:librar\w*|carnegie|reading\s+room|institute)\b", re.I)
# ⚠️ The trailing \b in an earlier version of the pattern above made "librar"
# never match "Library", so only Carnegie-titled files scored and the measured
# hit rate read 30% when it was 84%.
NAME_NEWER = re.compile(r"\b(new|modern|replacement|community hub)\b", re.I)
NAME_SKIP_EXT = (".pdf", ".tif", ".tiff", ".djvu", ".svg")
NAME_STOPWORDS = {"library", "public", "district", "central", "the"}
REVIEW = os.path.join(DATA, "uk_image_review.json")


def _name_candidates(title, name):
    """(confident, plausible) for one search hit."""
    t = title[5:] if title.startswith("File:") else title
    if t.lower().endswith(NAME_SKIP_EXT):
        return False, False
    if NAME_DETAIL.search(t) or not NAME_LIBRARYISH.search(t) or NAME_NEWER.search(t):
        return False, False
    # It must name the place itself, or "Carnegie Library" alone would match
    # any Carnegie library anywhere.
    words = [w for w in re.findall(r"[A-Za-z']{3,}", name)
             if w.lower() not in NAME_STOPWORDS]
    if words and not any(re.search(rf"\b{re.escape(w)}", t, re.I) for w in words):
        return False, False
    return bool(re.search(r"\bcarnegie\b", t, re.I)), True


def namesearch(rows, state):
    """Commons title search, for rows with neither a filename nor coordinates."""
    state.setdefault("name", {})
    pending = [r for r in rows
               if not r["image_file"].strip() and not r["lat"].strip()
               and r["_key"] not in state["name"]]
    log(f"stage 3  namesearch: {len(pending)} libraries with neither picture nor coordinates")
    for n, r in enumerate(pending, 1):
        d = get({"action": "query", "format": "json", "list": "search",
                 "srsearch": f'{r["name"]} library {r["region"]}',
                 "srnamespace": 6, "srlimit": 10})
        confident = plausible = None
        for h in (d or {}).get("query", {}).get("search", []) or []:
            sure, maybe = _name_candidates(h["title"], r["name"])
            if sure and confident is None:
                confident = h["title"]
            elif maybe and plausible is None:
                plausible = h["title"]
        state["name"][r["_key"]] = {"title": confident, "review": plausible}
        if n % 50 == 0 or n == len(pending):
            save_state(state)
            got = sum(1 for v in state["name"].values() if v and v.get("title"))
            log(f"         {n:>5}/{len(pending)}  confident {got}")
        time.sleep(DELAY)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["1", "2", "3"])
    ap.add_argument("--reset", action="store_true")
    args = ap.parse_args()

    if args.reset and os.path.exists(STATE):
        os.remove(STATE)
        log("state discarded")

    with open(ROSTER) as f:
        rows = [r for r in csv.DictReader(f) if r["kind"] == "public"]
    for i, r in enumerate(rows):
        r["_key"] = f"{i}:{r['name'][:40]}"
    log(f"roster: {len(rows)} public libraries")

    state = load_state()

    if args.stage in (None, "1"):
        titles = sorted({"File:" + r["image_file"] for r in rows if r["image_file"].strip()})
        resolve(titles, state)
    if args.stage in (None, "2"):
        geosearch(rows, state)
        extra = sorted({v["title"] for v in state["geo"].values() if v})
        if extra:
            resolve(extra, state)
    if args.stage in (None, "3"):
        namesearch(rows, state)
        extra = sorted({v["title"] for v in state.get("name", {}).values()
                        if v and v.get("title")})
        if extra:
            resolve(extra, state)

    out = []
    for r in rows:
        source = title = None
        if r["image_file"].strip():
            t = "File:" + r["image_file"]
            if state["imageinfo"].get(t):
                source, title = "wikipedia-list", t
        if source is None:
            g = state["geo"].get(r["_key"])
            if g and state["imageinfo"].get(g["title"]):
                source, title = "commons-geosearch", g["title"]
        if source is None:
            nm = state.get("name", {}).get(r["_key"])
            if nm and nm.get("title") and state["imageinfo"].get(nm["title"]):
                source, title = "commons-namesearch", nm["title"]
        meta = state["imageinfo"].get(title) if title else None
        who = (meta or {}).get("artist", "")
        out.append({
            "name": r["name"], "kind": r["kind"], "city": r["city"],
            "region": r["region"], "country": r["country"],
            "date_granted": r["date_granted"], "grant": r["grant"],
            "date_opened": r.get("date_opened", ""),
            "address": r["address"], "lat": r["lat"], "lon": r["lon"],
            "wikipedia_url": r.get("wikipedia_url", ""),
            "image_source": source or "",
            "image_title": title or "",
            "image_url": (meta or {}).get("url", ""),
            "photographer": who,
            "licence": (meta or {}).get("licence", ""),
            "licence_url": (meta or {}).get("licence_url", ""),
            "credit_page": (meta or {}).get("page", ""),
            "postable": ("yes" if (source and who and r["country"] not in HELD_COUNTRIES)
                         else "no"),
        })

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(out)

    have = [r for r in out if r["image_source"]]
    post = [r for r in out if r["postable"] == "yes"]
    log("")
    log(f"  libraries            {len(out):>5}")
    log(f"  with an image        {len(have):>5}  ({len(have)/len(out)*100:.1f}%)")
    # ⚠️ Listed explicitly, and stage 3 was missing from this tuple on its first
    # run: the totals were right and the breakdown silently under-reported by 76.
    for s in ("wikipedia-list", "commons-geosearch", "commons-namesearch"):
        log(f"      {s:<20} {sum(1 for r in have if r['image_source'] == s):>5}")
    log(f"  safe to post         {len(post):>5}  ({len(post)/len(out)*100:.1f}%)")
    log(f"  image but no credit  {len(have) - len(post):>5}")
    log(f"\nwritten to {OUT}")


if __name__ == "__main__":
    main()
