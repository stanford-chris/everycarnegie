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

Dates are rewritten in the style the library's own country uses: US libraries
get "February 2, 1903", everyone else "2 February 1903". The sources mix all
of "Feb 2, 1903", "January 20, 1908" and "2 Dec 1909" depending on which
Wikipedia list a row came from, so all three have to be parsed rather than
assumed.

Usage:
    python3 carnegie_post_preview.py            # six samples
    python3 carnegie_post_preview.py --count 12
    python3 carnegie_post_preview.py --seed 7
"""

import argparse
import csv
import hashlib
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

MONTHS = "January February March April May June July August September October November December".split()

# The date only, not the rest of the line: "Opened 19 Jan 1907, designed by
# Chicago architect Victor Andre Matteson" used to match whole, fail to parse,
# and go out with the raw date. A bare year is left to format_date's caller.
OPENED_DATE_RE = re.compile(
    r"^Opened\s+([A-Za-z]{3,9}\.? \d{1,2},? \d{4}|\d{1,2} [A-Za-z]{3,9}\.? \d{4})(.*)$",
    re.IGNORECASE)

# The region is the Wikipedia page title, which is not always a place name:
# "Washington (state)" disambiguates an article, and the continental pages give
# a continent where the row's own country column is the useful thing.
CONTINENTS = {"Africa", "Europe", "Oceania", "the Caribbean"}


def library_id(row):
    """Stable identity, so descriptions and post state survive a roster rebuild.

    Canonical here: carnegie_describe.py and everycarnegie_post.py both import
    this module already (for typographic()/build() etc.), so they take this
    rather than each keeping their own copy. A drifted copy would silently
    orphan every stored description or state entry keyed on the other.
    """
    key = f"{row['name']}|{row['city']}|{row['region']}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]


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


def format_date(raw, country=""):
    """'Feb 2, 1903' / 'January 20, 1908' / '2 Dec 1909' / '1886' -> a date fit
    to print, in the style the library's own country uses: US libraries get
    'February 2, 1903', everyone else 'day Month year', which is the
    convention this corpus's other 16 countries share.
    """
    raw = (raw or "").strip().rstrip(".")
    if not raw:
        return ""
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%d %b %Y", "%d %B %Y", "%b %d %Y"):
        try:
            d = datetime.strptime(raw, fmt)
            if country.strip() == "United States":
                return f"{MONTHS[d.month - 1]} {d.day}, {d.year}"
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
    """The Notes column arrives with the spacing artifacts of stripped markup."""
    s = re.sub(r"\[\s*\d+\s*\]", "", s or "")        # footnote markers
    # Page references left by a {{rp}} template: "Designed by Ernest
    # Coxhead. : 9, 12" — eight San Francisco rows carry them, and one has
    # prose after the numbers. Only after a full stop, so "Opened: 1921" and
    # "Official name: Andrew Carnegie Free Library" are left alone.
    s = re.sub(r"(?<=\.)\s*:\s*\d+(?:\s*,\s*\d+)*(?=\s|$)", "", s)
    s = re.sub(r"\s+([,.;])", r"\1", s)              # " , " -> ", "
    s = re.sub(r"\s+", " ", s).strip().rstrip(".")
    # Wikipedia's own "as of" stamp on a status — "still used as the public
    # library. (April 2011)", "No longer a public library. (2013)" — on 67
    # rows, and a dead "(info)" link label on six. Only after some prose:
    # four rows are nothing but "(1929)", and those are left as they are
    # rather than emptied.
    s = re.sub(r"(?<=\S)\s*\((?:(?:[A-Z][a-z]+ )?\d{4}|info)\)$", "", s)
    return s.rstrip(".")


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
    for i, ch in enumerate(s):
        if ch == '"':
            out.append("\u201c" if prev in " ([{\n" else "\u201d")
        elif ch == "'":
            # Opening position gets a left single quote, exactly as a double
            # quote does. The model labels signage in single quotes constantly
            # — 'Public Library', 'Parks & Recreation', 'LIBRARY' — 111 times
            # across the two alt-text stores, and closing both ends reads as a
            # typo. There is not one elision ('90s, 'tis) in either corpus, so
            # the only exception needed is the one below.
            #
            # ⚠️ The 's guard is not hypothetical. Wikipedia's Carnegie lists
            # carry two notes with a space before the possessive — "Thomas
            # Jefferson 's Monticello", "Pacific University 's first library" —
            # and without it those posts read "Jefferson ‘s", which is worse
            # than the straight apostrophe this whole change is fixing.
            rest = s[i + 1:i + 3]
            opening = prev in " ([{\n" and not (
                rest[:1] == "s" and not rest[1:2].isalpha())
            out.append("\u2018" if opening else "\u2019")
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

    # Name the country everywhere except the United States and the United
    # Kingdom. "Ontario" alone is ambiguous with Ontario, California, and this
    # corpus spans 17 countries. The two exemptions are for the same reason:
    # their subdivisions are widely known and unambiguous, and "Tecumseh,
    # Michigan, United States" reads like a postal address. England, Scotland,
    # Wales and Northern Ireland are countries in their own right and collide
    # with nothing, so "Airdrie Public Library, Scotland" is both shorter and
    # more natural than appending the state. region_of() already falls back to
    # the country on the continental pages, so the guard stops "Barberton,
    # South Africa, South Africa".
    country = row["country"].strip()
    if country and country not in ("United States", "United Kingdom"):
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


def compose(row, with_address=True):
    head = place(row)
    lines = [head + " 📚"]

    # Irish entries are identified by their street, so name and address are the
    # same string and the post said "Dingle" twice.
    address = row["address"].strip()
    if with_address and address and address.lower() != head.split(",")[0].strip().lower():
        lines.append(address)

    # Same pattern as everylibrary: a "📍 Map" line built from the roster's own
    # lat/lon, no new geocoding needed. Tied to with_address, not to whether an
    # address line was actually printed, so an Irish entry with no separate
    # address line still gets a pin; and it drops together with the address in
    # build()'s last-resort trim, since a pin with no address above it to
    # explain it is not worth the characters it costs.
    lat, lon = row.get("lat", "").strip(), row.get("lon", "").strip()
    if with_address and lat and lon:
        lines.append("📍 Map")
    lines.append("")

    granted = format_date(row["date_granted"], row.get("country", ""))
    grant = grant_amount(row["grant"])
    middle = []
    if grant and granted:
        today = in_todays_money(grant, row["date_granted"])
        middle.append(f"{grant} from Andrew Carnegie, {granted}"
                      + (f" ({today})" if today else ""))
    elif grant:
        middle.append(f"{grant} from Andrew Carnegie")
    elif granted:
        middle.append(f"Granted {granted}")
    # ⚠️ Britain has neither a grant nor a date granted. Its lists give the year
    # the building opened, and until 19 August 2026 nothing read it, so a
    # British post carried no date at all: "Teddington, England 📚 / brick and
    # stone construction". Used only as a fallback, so no American post changes:
    # those already carry the grant line, and their opening year is usually in
    # the note as well.
    elif row.get("date_opened", "").strip():
        middle.append(f"Opened {row['date_opened'].strip()}")
    # The note is NOT here: it is its own reply, see note_post(). 19 rows have
    # no grant line at all, and without this the post carries an empty middle
    # and goes out with a double blank line in it.
    if middle:
        lines.extend(middle)
        lines.append("")
    elif lines[-1] == "":
        pass
    lines.append(f"📷 {credit_name(row['photographer'])} · {row['licence']}")
    lines.append("")
    # #Libraries added 29 August 2026: an established niche feed (matching
    # everylibrary's own tag), where #CarnegieLibraries has no feed of its own
    # to speak of. See reference_bsky_discovery_hashtag_feeds. No per-state/
    # region tag (dropped 30 August 2026): a state hashtag doesn't match any
    # established feed the way #Libraries does, so it was pure noise on the post.
    tags = ["CarnegieLibraries", "Libraries"]
    lines.append(" ".join(f"#{t}" for t in tags))
    return typographic("\n".join(lines))


def build(row):
    """The first post: place, address, pin, grant, credit, tags.

    The note is never on it, however short — see note_post(). Without the
    note the longest first post in the corpus is 264 characters, but the
    last-resort trim stays for a row that has not been seen yet: the grant
    is the reason the post exists and the credit is a licence condition, so
    the address is the only thing that can go.
    """
    text = compose(row)
    if len(text) > LIMIT:
        text = compose(row, with_address=False)
    return text


# A sentence ends at . ! or ? followed by a space, except after an initial
# ("Frank L. Packard") or one of the abbreviations these notes actually use
# ("c. 1962", "St. Louis", "Mt. Pleasant", "Dr. Smith", "No. 2", "Jr."), each
# of which the naive split cut a sentence in half on.
_NOT_A_SENTENCE_END = re.compile(
    r"(?:\b[A-Z]|\b(?:St|Mt|Dr|Mrs?|Ms|Jr|Sr|No|Ave|Ft|Rd|Blvd|Co|Inc|c|ca|approx|vs|e\.g|i\.e))\.$")


def sentences(s):
    # A new sentence opens with a capital, a digit or a quote; "Steel Co. and
    # governed" is one sentence however the abbreviation list reads.
    parts = []
    for piece in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\u201c\u2018\"'(\[])", s):
        if parts and _NOT_A_SENTENCE_END.search(parts[-1]):
            parts[-1] += " " + piece
        else:
            parts.append(piece)
    return [p for p in parts if p]


def note_post(row, note):
    """The reply that says what became of the building, in full.

    Until 11 September 2026 the note rode on the first post, capped at 96
    characters "to keep it to one line" and then cut again by the 300-character
    limit, so it went out mid-sentence: "Originally a public library on the
    Ohio…" on Athens, Ohio, with 38 characters still unused. His call that day:
    the note is a reply of its own, always, whether or not it would have fit.

    A reply has the whole 300 to itself and only 35 of the 1,004 notes exceed
    that. Those lose a whole SENTENCE at a time from the end, never a word,
    and the ellipsis is the last resort, for a note whose first sentence alone
    is over the limit — none in the corpus as of that date, so if one appears
    it is a data problem worth looking at rather than a trim.

    Returns "" for a row with no note, and the caller posts no reply.
    """
    if not note:
        return ""
    # These notes are the tail of a Wikipedia bullet, so they begin
    # mid-sentence in lower case: "brick and stone construction".
    printable = note[0].upper() + note[1:] if note[:1].islower() else note
    # ⚠️ Nine US rows carry a Notes column that is nothing but an opening
    # date ("Opened 29 Feb 1916"), copied verbatim from Wikipedia's own
    # per-state tables — Illinois writes "29 Feb 1916", Iowa and South
    # Dakota already write "March 21, 1906". Never reformatted before, so
    # a US post could carry a grant date in house style beside a raw,
    # differently-styled opening date (caught 3 September 2026: Marion,
    # Illinois showed "February 13, 1909" next to "Opened 29 Feb 1916").
    # Reuse format_date() so this gets the same country-aware treatment.
    opened = OPENED_DATE_RE.match(printable)
    if opened:
        formatted = format_date(opened.group(1), row.get("country", ""))
        if formatted:
            printable = f"Opened {formatted}{opened.group(2)}"
    if not printable.endswith((".", "!", "?", "…")):
        printable += "."
    text = typographic(printable)
    if len(text) <= LIMIT:
        return text
    parts = sentences(printable)
    while len(parts) > 1:
        parts = parts[:-1]
        text = typographic(" ".join(parts))
        if len(text) <= LIMIT:
            return text
    cut = parts[0][:LIMIT - 1].rsplit(" ", 1)[0].rstrip(",;:")
    return typographic(cut + "…")


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

    def pair(r):
        note = clean_note(notes.get((r["name"], r["city"], r["region"]), ""))
        return build(r), note_post(r, note), note

    for r in rows[:args.count]:
        text, reply, _ = pair(r)
        flag = "" if len(text) <= LIMIT else "   ⚠️ OVER LIMIT"
        print("─" * 58)
        print(text)
        print(f"[{len(text)} chars]{flag}")
        if reply:
            print(f"  ↳ {reply}")
            print(f"  [reply {len(reply)} chars]")
        print(f"[img] {r['image_url'][:88]}")
    print("─" * 58)

    # How often would the limit bite across the whole corpus?
    longest = longest_reply = over = over_reply = trimmed = ellipsis = 0
    for r in rows:
        text, reply, note = pair(r)
        longest = max(longest, len(text))
        over += len(text) > LIMIT
        if reply:
            longest_reply = max(longest_reply, len(reply))
            over_reply += len(reply) > LIMIT
            trimmed += len(reply) < len(typographic(note))
            ellipsis += reply.endswith("…")
    print(f"across all {len(rows)} postable rows: longest first post {longest} chars, "
          f"{over} over the {LIMIT} limit; longest reply {longest_reply} chars, "
          f"{over_reply} over, {trimmed} trimmed by a sentence, {ellipsis} cut mid-sentence")


if __name__ == "__main__":
    main()
