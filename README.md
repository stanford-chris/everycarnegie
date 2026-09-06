# everycarnegie

A roster of the library buildings Andrew Carnegie paid for, built from Wikipedia's
per-state and per-country lists.

Carnegie funded **2,509 library buildings between 1883 and 1929**: 1,689 in the
United States, 660 in Britain and Ireland, 125 in Canada and 25 across ten other
countries. Wikidata knows only 703 of them, so it cannot serve as the roster.

## What the harvest produces

`data/carnegie_roster.csv`, from 57 list pages:

| | |
|---|---|
| Public libraries | **2,151** |
| Academic libraries, kept separate | 112 |
| Countries | 17 |
| With grant amount | 92% |
| With date granted | 89% |
| With an address | 85% |
| With an image on the page | 63% |
| With coordinates | 31% |

United States 1,681, United Kingdom 245, Canada 125, Ireland 56, New Zealand 18,
South Africa 12,
Australia 4, then single figures across Trinidad and Tobago, Mauritius,
Seychelles, Barbados, Dominica, Guyana, Puerto Rico, Saint Lucia and
Saint Vincent.

Two independent checks say the US harvest is right: 1,681 against the documented
1,689, and Indiana at 164, the figure Indiana is known for. Canada matches its
documented 125 exactly.

⚠️ Britain arrived on 19 August 2026 and is **partial by nature**: 245 public
rows against a documented 660 for Britain and Ireland. It comes from bullet
lists rather than tables, so it carries no addresses, no coordinates and no
images, and 39 of the 247 have no date. See the Britain section below.

```bash
python3 carnegie_roster.py             # harvest and write the csv
python3 carnegie_roster.py --refetch   # ignore the page cache
python3 carnegie_roster.py --stdout    # report only, write nothing
```

## What a post carries

```
Eufaula Carnegie Library, Alabama 📚
217 N Eufaula Ave.
📍 Map

$10,000 from Andrew Carnegie, February 2, 1903 (about $358,000 today)
Contributing building in Seth Lore and Irwinton Historic District

📷 Rivers Langley; SaveRivers · CC BY-SA 3.0

#CarnegieLibraries #Libraries
```

**"📍 Map" links the row's own `lat`/`lon` to Google Maps** (`https://www.google.com/maps?q=<lat>,<lon>`),
when the row has them — only 31% do (see the coverage table above), so most posts carry no pin.
It follows the address and shares its fate: tied to `with_address` rather than to whether an
address line actually printed, and dropped together with the address if `build()`'s last-resort
length trim needs the room.

**The grant in today's money** comes from `data/cpi.json`, the Minneapolis
Fed's annual index, which splices the historical series onto CPI-U. CPI-U
begins in 1913 and most of these grants predate it, so a CPI-U-only table
would silently fail on the majority. The file records its source and retrieval
date; the wording is always "about", because a CPI conversion is one
defensible comparison rather than the answer.

**Two links, where everylibrary carries one.** The photographer's name points
at the Commons file page, which satisfies CC BY-SA 4.0 s3(a)(2). The library's
name points at its Wikipedia article on the 25% of rows that have one, and
only the name is linked, never the region appended after it.

⚠️ That 25% is the honest figure. Taking the link from the city cell as well
lifts it to 91%, and those links go to the **town** — "Curepipe" the place,
not its library. A post whose title links to a town article is quietly wrong,
so the link is only ever taken from a genuine library-name column.

**The date reads in the library's own country's style**, via `format_date()`
in `carnegie_post_preview.py`: United States rows get "February 2, 1903";
every other country gets "2 February 1903", the day-month-year convention the
other 16 countries in this corpus share. Changed 30 August 2026 from a single
UK-style rendering used everywhere.

⚠️ **`HEADER_MAP` in `carnegie_roster.py` mapped only "notes" and "status" to
the notes column until 30 August 2026, and Iowa's own page uses neither.**
Iowa's tables header the column "Remarks", so all 108 of its rows — public and
academic together — carried an empty note, silently dropping exactly the
"razed in 1968" / "now the Cedar Rapids Museum of Art" / "demolished for
construction of a new library" sentences a post exists to carry. `"remarks"`
is now mapped too. Re-run `carnegie_roster.py` after any Wikipedia list page
is added or refetched, and check the header list below for another
unrecognised header before assuming the notes column is complete:
```bash
python3 -c "
import glob, re
from bs4 import BeautifulSoup
headers = set()
for fn in glob.glob('data/pages/*.html'):
    soup = BeautifulSoup(open(fn, encoding='utf-8').read(), 'html.parser')
    for table in soup.find_all('table', class_=re.compile('wikitable')):
        row = table.find('tr')
        if row:
            headers |= {re.sub(r'\s+',' ', re.sub(r'\[\s*\d+\s*\]','',th.get_text())).strip().lower()
                        for th in row.find_all('th')}
print(sorted(headers))
"
```

## Posting

`everycarnegie_post.py` posts one library from `data/carnegie_images.csv` in a
fixed shuffled order (`data/post_state.json` tracks position and posted ids).
`--pin` instead refreshes the pinned "Sources and credits" post, keeping its
"N of 2,509" line in sync with the roster.

Scheduled via launchd:

- **`com.chrisstanford.everycarnegie`** — the daily poster, twice a day
  (11 p.m. and 9 a.m. Asia/Seoul, timed for a mostly-American audience).
- **`com.chrisstanford.everycarnegie-launch`** — `everycarnegie_launch.sh`,
  the one-off opening thread (29 August 2026, spent). Pins the credits note,
  posts the two-post opening, then removes its own launchd job.
- **`com.chrisstanford.everycarnegiemonthly`** — `everycarnegie_monthly.sh`,
  a monthly re-sweep: re-check for photographs on libraries that had none
  (`carnegie_images.py --recheck-misses`), describe whatever turns up
  (`carnegie_describe.py`), then refresh the pinned credits count.

`shelf_life_followup.sh` is a separate one-off (15 September 2026): a
reminder email about the Britain gazetteer licensing request below. It
self-deletes after sending.

## ⚠️ Britain is missing, and here is what it would take

**The 660 British Carnegie libraries are not in this roster.** Wikipedia's Europe
page carries Ireland as a proper table, which is captured; Britain is not in
table form and the harvester reads tables.

The wikitext is not unparseable prose, it just isn't a table:

- **Scotland, Wales and Northern Ireland are one library per bullet**, with a
  name, a year and usually a wikilink:
  `* [[Airdrie Public Library]] 1894 and 1925`
- **England is a two-level list**, branches nested under their city:
  `* [[Coventry]]` then `** [[Earlsdon]] Library 1913.`

A second parser for lists, alongside the existing one for tables, yields
**about 225 entries**: England 92
top-level plus 66 nested, Scotland 30, Wales 32, Northern Ireland 5.

⚠️ **And a gazetteer nobody had found is on a public endpoint.** The AHRC
"Shelf-Life" project at Cardiff, *Carnegie Libraries of Britain*, serves its
whole map from an ArcGIS FeatureServer: **621 records**, built from research
lists supplied by the Carnegie UK Trust plus the statutory lists. 128 were never
built, leaving 493 buildings, 451 still standing, 492 of them with coordinates,
architects on 65%. That is better data than the American rows the bot already
posts, which carry coordinates on 31%.

⚠️ **It is CC BY-NC-SA 4.0.** The feature layer's own metadata carries no
copyright text, which reads as unlicensed; the project's site is explicit, and
requires the credit `© [creator] Cardiff University AHRC "Shelf Life" project
[AH/P002587/1]`. Checking the endpoint is not checking the licence.

⚠️ **CC BY-SA and CC BY-NC-SA cannot both be satisfied by one file, and the
UK's separate database right raises the bar further.** ShareAlike runs both
directions — BY-SA forbids adding the non-commercial restriction, BY-NC-SA
forbids dropping it — so the gazetteer's rows cannot be merged into
`carnegie_roster.csv` (CC BY-SA) under either licence. The distinction that
saves the two-file approach is Adapted Material versus a Collection: two
files kept apart, each under its own licence, read side by side at run time,
is a collection and stays inside both; one CSV with the rows interleaved is
an adaptation and does not. And since facts alone are not copyrightable but a
compiled, verified database can carry the UK's separate database right, that
is the stronger reason to ask rather than assume either way.

The ask is therefore for the gazetteer data alone, under CC BY-SA or CC BY.
Letter drafted in `shelf_life_email.py`.

Its photographs are all "© Oriel Prizeman" and reserved. That costs nothing: the
bot's pictures come from Commons and have to be freely licensed to post at all.

| Source | Yield | Verdict |
|---|---|---|
| Wikipedia's Europe list, parsed as lists | ~225 | ⭐ do this: same CC BY-SA licence as the rest, asks nobody |
| Carnegie Libraries of Britain gazetteer | 621 records, 493 built | ⭐ ask: authoritative, but CC BY-NC-SA, which the roster cannot absorb |
| Historic England / HES / Cadw statutory lists | listed buildings only | Open Government Licence. Verification, not a roster |
| Columbia's digitised Carnegie Corporation records | primary source | settles a disputed date; not for bulk |
| Miller, *Carnegie Grants for Library Buildings 1890–1917* (1943) | authoritative | print only |
| Wikidata | 66 UK items, mostly hockey clubs | rejected, re-confirmed 19 Aug 2026 |
| Commons subcategories | ~79 | rejected, unchanged |
| everylibrary's UK corpus, matched on name | 5 | rejected, unchanged |

⚠️ **Every name-based approach fails for one structural reason**, and it is why
Wikidata and the name-match come back near zero: **British Carnegie libraries are
named after their town, not after Carnegie.** Renfrew's is Renfrew Library.

The full working, with counts and the licence question set out, is in
`britain_options.py`:

```bash
python3 britain_options.py && open data/britain_options.html
```

## Does the premise hold? `carnegie_verify.py`

Every row is Wikipedia's claim that a building was Carnegie-funded, and nothing
tested that until 19 August 2026.

```bash
python3 carnegie_verify.py            # report only
python3 carnegie_verify.py --apply    # also blank unsupported links
```

Three checks. **Aggregate**: 1,681 US against a documented 1,689, Canada 125
exactly, Indiana 164. **Shape**: no duplicate rows; one name that is not a
library, the Kish Bank lighthouse, and Ireland is held back anyway.
**Corroboration**: for the 23% of rows that link a Wikipedia article, fetch that
article and look for the word Carnegie. It is written by different editors from
the list that named the building, so agreement is real evidence.

**9 of 499 articles never mention Carnegie**, and the script blanks those links
rather than dropping the rows: a library whose article turns out to be about a
park is still a Carnegie library, it is the link that is wrong. Two were plainly
wrong — Seward Park pointed at the park and Charleston at a 1748 subscription
library — and about four are probably the right building with an incomplete
article. The check cannot tell those apart, so it blanks all nine and loses four
useful links out of 1,262.

⚠️ **Always request `redirects=1`.** Asking the API for an article by title
without it returns the redirect page, not its target, and a redirect's entire
content is one line — so a redirected library reads as an empty article with
no Carnegie mention, inflating the miss count fivefold.

⚠️ **77% of rows link no article at all**, and for them the only evidence is the
list row itself. A clean run means the checkable quarter checks out, not that
the roster is verified.

## ⚠️ Every generated page must declare its charset, first

Safari reads a local `file://` page with no charset declaration as Latin-1, so
every curly quote renders as `â€™`, every en dash as `â€“` and every ⚠️ as
`âš ï¸`. Six of these pages shipped that way before it was noticed on 19 August
2026. The declaration has to come **before** `<title>`, or the title is decoded
before the parser reaches it:

```python
out = ['<meta charset="utf-8">', f"<title>…</title>", …]
```

`britain_options.py`, `carnegie_sample_page.py`, `launch_thread.py`,
`launch_thread_stress.py`, `preview_all.py` and `avatar/make_avatar_options.py`
all carry it now. Anything new that writes HTML needs it too: the files
themselves are written UTF-8, so this is purely a declaration problem and it
does not show up until someone opens one in Safari.

## Header parsing gotchas, in `header_text`

Three things bite header matching, and each one silently drops a whole column
rather than erroring — a file that "looks complete" (right row count) can still
be missing data, so check per-column fill rates after adding or refetching a
page. **Headers wrap with `<br>`** (e.g. "City or<br>town"), so `<br>` needs an
explicit separator or "or" and "town" fuse into one unmatched key. **Footnote
markers use `<sup>`** (`Date granted[1]`), which must be stripped outright
rather than pattern-matched: once a `<br>` separator inserts whitespace, a
`\[\d+\]` regex no longer catches `[ 1 ]`. **Parenthetical qualifiers** like
Canada's `Grant amount (US$)` need stripping generally rather than matching
literally, for the same whitespace-insertion reason.

## Two more things worth knowing

**Public and academic are kept apart.** Carnegie funded college libraries as
well as public ones, and Wikipedia lists them in a second table on the same
page. They are distinguishable only by that table's header saying "Institution"
where the public one says "Library", so the distinction lives in the `kind`
column instead of being silently merged.

**Outside the US there is no library-name column at all.** Africa and the
Caribbean identify a library by its "Community", Oceania by "Town", Ireland by
"Location and street". The town is the name in those lists, so the parser falls
back to it rather than discarding the table.
