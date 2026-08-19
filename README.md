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
| Public libraries | **1,910** |
| Academic libraries, kept separate | 106 |
| Countries | 16 |
| With grant amount | 92% |
| With date granted | 89% |
| With an address | 85% |
| With an image on the page | 63% |
| With coordinates | 31% |

United States 1,685, Canada 125, Ireland 56, New Zealand 18, South Africa 12,
Australia 4, then single figures across Trinidad and Tobago, Mauritius,
Seychelles, Barbados, Dominica, Guyana, Puerto Rico, Saint Lucia and
Saint Vincent.

Two independent checks say the US harvest is right: 1,685 against the documented
1,689, and Indiana at 164, the figure Indiana is known for. Canada matches its
documented 125 exactly.

```bash
python3 carnegie_roster.py             # harvest and write the csv
python3 carnegie_roster.py --refetch   # ignore the page cache
python3 carnegie_roster.py --stdout    # report only, write nothing
```

## What a post carries

```
Eufaula Carnegie Library, Alabama 📚
217 N Eufaula Ave.

$10,000 from Andrew Carnegie, 2 February 1903 (about $358,000 today)
Contributing building in Seth Lore and Irwinton Historic District

📷 Rivers Langley; SaveRivers · CC BY-SA 3.0

#CarnegieLibraries #Alabama
```

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

## ⚠️ Britain is missing, and here is what it would take

**The 660 British Carnegie libraries are not in this roster.** Wikipedia's Europe
page carries Ireland as a proper table, which is captured; Britain is not in
table form and the harvester reads tables.

⚠️ **This section used to say the British entries were unparseable prose and
that four sources had been tried and all failed. Both halves were wrong, and the
error was load-bearing: it read as an argument for not looking again.** Checked
against the live wikitext on 19 August 2026:

- **Scotland, Wales and Northern Ireland are one library per bullet**, with a
  name, a year and usually a wikilink:
  `* [[Airdrie Public Library]] 1894 and 1925`
- **England is a two-level list**, branches nested under their city:
  `* [[Coventry]]` then `** [[Earlsdon]] Library 1913.`

Not crammed prose. It reads that way only if the markup is stripped before it is
parsed, which is probably where the claim came from. A second parser for lists,
alongside the existing one for tables, yields **about 225 entries**: England 92
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

**CC BY-SA and CC BY-NC-SA are one-way incompatible**, so these rows cannot be
merged into `carnegie_roster.csv`, which is Wikipedia-derived and CC BY-SA:
doing so would drag 1,910 rows into a non-commercial licence they are not free
to take. The ask is therefore for the gazetteer data alone, under CC BY-SA or
CC BY. Letter drafted in `shelf_life_email.py`; the fallback is a separate file,
separately licensed and separately credited.

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

## Three parsing traps, all of the same species

Each produced a file that looked complete and was quietly missing data. They are
commented at `header_text` because the naive version of each is the obvious one.

- **Headers wrap with `<br>`.** Read without a separator, "City or<br>town"
  fuses into `city ortown` and matches no key. The first run lost the grant
  amount, the city and both dates on every US page while reporting 1,916 rows
  and looking like a success.
- **Adding the separator then breaks the footnote strip.** `Date granted[1]`
  becomes `date granted [ 1 ]`, which a `\[\d+\]` pattern no longer catches, and
  `date_granted` fell from 121 rows to 39. The `<sup>` elements are now removed
  outright rather than matched.
- **Parenthetical qualifiers space out too.** Canada's `Grant amount (US$)`
  arrives as `grant amount ( us$ )`: zero of 125 rows. Parentheses are now
  stripped generally, not matched literally.

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
