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
import json
import os
import random
import re
from datetime import datetime
from pathlib import Path

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


_CPI = None


def cpi():
    """Annual CPI, 1800 onward, cached from data/cpi.json.

    CPI-U begins in 1913 and most of these grants predate it, so the series is
    the Minneapolis Fed's, which splices the historical index onto CPI-U. The
    file records its source and retrieval date: an inflation figure invented
    from memory would be fluent, plausible and wrong, which is the failure this
    project keeps finding.
    """
    global _CPI
    if _CPI is None:
        with (Path(__file__).resolve().parent / "data" / "cpi.json").open() as f:
            d = json.load(f)
        _CPI = ({int(k): v for k, v in d["index"].items()}, d["base_year"])
    return _CPI


def year_of(raw):
    m = re.search(r"(18|19)\d{2}", raw or "")
    return int(m.group(0)) if m else None


def in_todays_money(grant, raw_date):
    """'$10,000', 1903 -> 'about $358,000 today'. Empty when it cannot be done.

    Deliberately vague wording. This is a CPI conversion, which is one of
    several defensible ways to compare 1903 with now, and "about" is doing
    honest work rather than hedging.
    """
    idx, base = cpi()
    year = year_of(raw_date)
    amount = re.sub(r"[^\d.]", "", grant or "")
    if not year or not amount or year not in idx or base not in idx:
        return ""
    now = float(amount) * idx[base] / idx[year]
    if now >= 1_000_000:
        millions = now / 1_000_000
        shown = f"${millions:.0f} million" if millions >= 10 else f"${millions:.1f} million"
    else:
        shown = f"${round(now, -3):,.0f}"
    return f"about {shown} today"


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


def grant_amount(raw):
    """'$10,000' / '10,000' / '—' -> a printable amount, or nothing.

    Wikipedia writes an em dash where the sum is unknown, which 106 rows carry,
    and "— from Andrew Carnegie, 18 January 1910" is not a sentence. The 38
    bare numbers are Canada's, whose column header says (US$) and so needs the
    symbol adding rather than inventing a different currency.
    """
    s = re.sub(r"\[\s*\d+\s*\]", "", raw or "").strip()
    if not re.search(r"\d", s):
        return ""
    s = s.strip("()")
    s = re.sub(r"^US\$?\s*", "", s, flags=re.I)
    if " " in s:                                  # "10,000 15,500": two grants, ambiguous
        return ""
    return s if s.startswith("$") else "$" + s


def clean_note(s):
    """The Notes column arrives with the spacing artefacts of stripped markup."""
    s = re.sub(r"\[\s*\d+\s*\]", "", s or "")        # footnote markers
    s = re.sub(r"\s+([,.;])", r"\1", s)              # " , " -> ", "
    s = re.sub(r"\s+", " ", s).strip().rstrip(".")
    if len(s) > NOTE_MAX:
        cut = s[:NOTE_MAX].rsplit(" ", 1)[0]
        s = cut + "…"
    return s


def typographic(s):
    """Curly quotes and apostrophes, which is the house style.

    ⚠️ Whatever this does to the post text must also be done to the strings the
    poster searches for when attaching links. It finds the photographer's name
    and the library's name inside the finished text to place the facets, and
    nine photographers and one library in this corpus carry an apostrophe —
    Bobak Ha'Eri, Saint Gabriel's Park. Curling the haystack and not the needle
    drops the credit link on those posts, silently, and a missing credit on a
    CC BY-SA photograph is a licence breach rather than a typo.
    """
    out, prev = [], " "
    for ch in s:
        if ch == '"':
            out.append("\u201c" if prev in " ([{\n" else "\u201d")
        elif ch == "'":
            out.append("\u2019")
        else:
            out.append(ch)
        prev = ch
    return "".join(out)


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
    if country and country != "United States":
        parts.append(country)

    # "Blackrock, Dublin" in a region called Dublin gives "Blackrock, Dublin,
    # Dublin". Drop repeats, keeping the first occurrence, because the name
    # itself already carries the qualifier.
    seen, out = set(), []
    for part in parts:
        if part and part.lower() not in seen:
            seen.add(part.lower())
            out.append(part)
    return ", ".join(out)


def credit_name(who):
    """A person's name, out of whatever Commons holds in its Artist field.

    Four shapes turn up and all of them read badly in a credit line:
    'User:Magicpiano', 'Armona at en.wikipedia', 'The original uploader was GHe
    at English Wikipedia.', and names trailed by a request to the reader —
    'CZmarlin — Christopher Ziemnowicz, a photo credit would be appreciated'.
    The name is kept; the plumbing around it is not. The licence still requires
    the name, and the file page carries the unedited original.
    """
    who = (who or "").strip()
    who = re.sub(r"^\s*the original uploader was\s+", "", who, flags=re.I)
    who = re.sub(r"\s+at\s+(en\.wikipedia|english\s+wikipedia).*$", "", who, flags=re.I)
    who = re.sub(r"^\s*(User|user)\s*:\s*", "", who)
    who = re.split(r"\s+[—–-]\s+", who)[0]          # drop trailing real-name gloss/requests
    who = re.sub(r",\s*(a\s+)?photo credit.*$", "", who, flags=re.I)
    who = re.sub(r"\s*\(talk\)\s*", " ", who, flags=re.I)
    # Commons sometimes stores the Artist field doubled, most often as
    # "Unknown authorUnknown author": the template renders the value twice and
    # a tag strip runs the two copies together.
    m = re.fullmatch(r"(.{4,}?)\1", who.strip())
    if m:
        who = m.group(1)
    who = re.sub(r"\s+", " ", who).strip(" .,;")
    return who


def compose(row, note, with_address=True):
    head = place(row)
    lines = [head + " 📚"]

    # Irish entries are identified by their street, so name and address are the
    # same string and the post said "Dingle" twice.
    address = row["address"].strip()
    if with_address and address and address.lower() != head.split(",")[0].strip().lower():
        lines.append(address)
    lines.append("")

    granted, grant = uk_date(row["date_granted"]), grant_amount(row["grant"])
    middle = []
    if grant and granted:
        today = in_todays_money(grant, row["date_granted"])
        middle.append(f"{grant} from Andrew Carnegie, {granted}"
                      + (f" ({today})" if today else ""))
    elif grant:
        middle.append(f"{grant} from Andrew Carnegie")
    elif granted:
        middle.append(f"Granted {granted}")
    if note:
        middle.append(note)
    # 19 rows have neither a grant nor a note. Without this the post carries an
    # empty middle and goes out with a double blank line in it.
    if middle:
        lines.extend(middle)
        lines.append("")
    elif lines[-1] == "":
        pass
    lines.append(f"📷 {credit_name(row['photographer'])} · {row['licence']}")
    tag = re.sub(r"[^A-Za-z]", "", region_of(row))
    lines.append("")
    lines.append(f"#CarnegieLibraries #{tag}" if tag else "#CarnegieLibraries")
    return typographic("\n".join(lines))


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
