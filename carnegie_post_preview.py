#!/usr/bin/env python3
"""
carnegie_post_preview.py — render sample posts from the roster, post nothing.

The shape follows everylibrary: place, address, then the credit, with the
photograph carrying its own A.I.-written description. What differs is the line
in the middle, which is the whole reason this bot is not just everylibrary with
a different corpus:

    $10,000 from Andrew Carnegie, 2 February 1903
    Closed c.1962, now artist studios

The grant and the date come from Wikipedia's tables and are present on ~90% of
the roster. The second line is the "Notes" column, which is where the interest
lives: what the building became. A museum, artist studios, a restaurant, or
nothing at all because it was demolished in 1978.

Dates are rewritten to UK style. The sources are American and write "Feb 2,
1903"; the house style is "2 February 1903", and the lists also carry British
and New Zealand orderings, so all three have to be parsed rather than assumed.

Usage:
    python3 carnegie_post_preview.py            # six samples
    python3 carnegie_post_preview.py --count 12
    python3 carnegie_post_preview.py --seed 7
"""

import argparse
import csv
import os
import random
import re
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
IMAGES = os.path.join(DATA, "carnegie_images.csv")
ROSTER = os.path.join(DATA, "carnegie_roster.csv")

LIMIT = 300          # Bluesky's post length
NOTE_MAX = 96        # keep the note to one line

MONTHS = "January February March April May June July August September October November December".split()

# The region is the Wikipedia page title, which is not always a place name:
# "Washington (state)" disambiguates an article, and the continental pages give
# a continent where the row's own country column is the useful thing.
CONTINENTS = {"Africa", "Europe", "Oceania", "the Caribbean"}


def uk_date(raw):
    """'Feb 2, 1903' / 'January 20, 1908' / '2 Dec 1909' / '1886' -> UK style."""
    raw = (raw or "").strip().rstrip(".")
    if not raw:
        return ""
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%d %b %Y", "%d %B %Y", "%b %d %Y"):
        try:
            d = datetime.strptime(raw, fmt)
            return f"{d.day} {MONTHS[d.month - 1]} {d.year}"
        except ValueError:
            pass
    m = re.fullmatch(r"(18|19)\d{2}", raw)
    return raw if m else ""          # a bare year is fine; anything odder is dropped


def clean_note(s):
    """The Notes column arrives with the spacing artefacts of stripped markup."""
    s = re.sub(r"\[\s*\d+\s*\]", "", s or "")        # footnote markers
    s = re.sub(r"\s+([,.;])", r"\1", s)              # " , " -> ", "
    s = re.sub(r"\s+", " ", s).strip().rstrip(".")
    if len(s) > NOTE_MAX:
        cut = s[:NOTE_MAX].rsplit(" ", 1)[0]
        s = cut + "…"
    return s


def region_of(row):
    """A place name fit to print, not the article title it came from."""
    region = re.sub(r"\s*\([^)]*\)", "", row["region"].strip()).strip()
    if region in CONTINENTS or not region:
        return row["country"].strip()
    return region


def place(row):
    """'Tecumseh, Michigan'. Where the list gave a real library name that is not
    just the town again, keep it: 'Springfield Central, Massachusetts'."""
    name, city = row["name"].strip(), row["city"].strip()
    region = region_of(row)
    head = name if name and name.lower() != city.lower() else city or name
    parts = [head]
    if region and region.lower() != head.lower():
        parts.append(region)

    # Name the country everywhere except the United States. "Ontario" alone is
    # ambiguous with Ontario, California, and this corpus spans 16 countries.
    # The US is exempted because its states are widely known and "Tecumseh,
    # Michigan, United States" reads like a postal address. region_of() already
    # falls back to the country on the continental pages, so the guard stops
    # "Barberton, South Africa, South Africa".
    country = row["country"].strip()
    if country and country != "United States" and country.lower() not in {p.lower() for p in parts}:
        parts.append(country)
    return ", ".join(parts)


def credit_name(who):
    """Commons stores uploader names with a namespace prefix. 'User:Magicpiano'
    is not how you credit somebody in a sentence."""
    who = re.sub(r"^\s*(User|user)\s*:\s*", "", who or "").strip()
    return re.sub(r"\s+", " ", who)


def compose(row, note, with_address=True):
    lines = [place(row) + " 📚"]
    if with_address and row["address"].strip():
        lines.append(row["address"].strip())
    lines.append("")

    granted, grant = uk_date(row["date_granted"]), row["grant"].strip()
    if grant and granted:
        lines.append(f"{grant} from Andrew Carnegie, {granted}")
    elif grant:
        lines.append(f"{grant} from Andrew Carnegie")
    elif granted:
        lines.append(f"Granted {granted}")
    if note:
        lines.append(note)

    lines.append("")
    lines.append(f"📷 {credit_name(row['photographer'])} · {row['licence']}")
    tag = re.sub(r"[^A-Za-z]", "", region_of(row))
    lines.append("")
    lines.append(f"#CarnegieLibraries #{tag}" if tag else "#CarnegieLibraries")
    return "\n".join(lines)


def build(row, note):
    """Fit the post to the limit by giving up the least valuable thing first.

    The grant and the credit are never sacrificed: the grant is the reason the
    post exists and the credit is a licence condition. So the note shortens,
    then goes, and only then does the address. Eight of 1,246 need any of this.
    """
    text = compose(row, note)
    if len(text) <= LIMIT:
        return text

    n = note
    while n and len(text) > LIMIT:
        cut = n[:-8].rsplit(" ", 1)[0] if len(n) > 12 else ""
        n = (cut + "…") if cut else ""
        text = compose(row, n)
    if len(text) > LIMIT:
        text = compose(row, n, with_address=False)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=6)
    ap.add_argument("--seed", type=int, default=3)
    args = ap.parse_args()

    with open(ROSTER) as f:
        notes = {(r["name"], r["city"], r["region"]): r.get("notes", "")
                 for r in csv.DictReader(f)}
    with open(IMAGES) as f:
        rows = [r for r in csv.DictReader(f) if r["postable"] == "yes"]

    random.Random(args.seed).shuffle(rows)
    over = 0
    for r in rows[:args.count]:
        note = clean_note(notes.get((r["name"], r["city"], r["region"]), ""))
        text = build(r, note)
        flag = "" if len(text) <= LIMIT else "   ⚠️ OVER LIMIT"
        over += len(text) > LIMIT
        print("─" * 58)
        print(text)
        print(f"[{len(text)} chars]{flag}")
        print(f"[img] {r['image_url'][:88]}")
    print("─" * 58)

    # How often would the limit bite across the whole corpus?
    longest = 0
    for r in rows:
        t = build(r, clean_note(notes.get((r["name"], r["city"], r["region"]), "")))
        longest = max(longest, len(t))
        over += 0
    too_long = sum(1 for r in rows
                   if len(build(r, clean_note(notes.get((r["name"], r["city"], r["region"]), "")))) > LIMIT)
    print(f"across all {len(rows)} postable rows: longest {longest} chars, "
          f"{too_long} over the {LIMIT} limit")


if __name__ == "__main__":
    main()
