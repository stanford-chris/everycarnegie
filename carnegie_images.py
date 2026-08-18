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

There is no Geograph stage. Geograph covers Britain and Ireland, and this roster
is overwhelmingly American: it supplied a third of everylibrary's coverage and
would supply almost none here.

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

FIELDS = ["name", "kind", "city", "region", "country", "date_granted", "grant",
          "address", "lat", "lon", "image_source", "image_title", "image_url",
          "photographer", "licence", "licence_url", "credit_page", "postable"]


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["1", "2"])
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
        meta = state["imageinfo"].get(title) if title else None
        who = (meta or {}).get("artist", "")
        out.append({
            "name": r["name"], "kind": r["kind"], "city": r["city"],
            "region": r["region"], "country": r["country"],
            "date_granted": r["date_granted"], "grant": r["grant"],
            "address": r["address"], "lat": r["lat"], "lon": r["lon"],
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
    for s in ("wikipedia-list", "commons-geosearch"):
        log(f"      {s:<20} {sum(1 for r in have if r['image_source'] == s):>5}")
    log(f"  safe to post         {len(post):>5}  ({len(post)/len(out)*100:.1f}%)")
    log(f"  image but no credit  {len(have) - len(post):>5}")
    log(f"\nwritten to {OUT}")


if __name__ == "__main__":
    main()
