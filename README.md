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

## ⚠️ Britain is missing, and not by oversight

**The 660 British Carnegie libraries are not in this roster and cannot be got
from these lists.** Wikipedia's Europe page carries Ireland as a proper table,
which is captured, but England, Scotland, Wales and Northern Ireland are *prose
bullet lists*: 103 England bullets with several libraries crammed into each
("Birmingham. Aston Cross, 1903. Bartley Green 1905…"), no addresses and no
coordinates.

Four sources were tried and none comes close:

| Source | UK and Ireland found |
|---|---|
| Wikipedia prose bullets | ~187 bullets, England's compound |
| Wikipedia categories | 57 articles |
| Commons subcategories | ~79 buildings |
| Wikidata | 78 UK items, 70 photographed |
| `everylibrary`'s UK corpus, matched on the name | 5 |

Name-matching against the sibling project fails because British Carnegie
libraries are almost always named after their town, not after Carnegie.

So the roster is 1,910 of 2,509, and the missing quarter is almost entirely
British. Adding it is a research problem, not a parsing one.

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
