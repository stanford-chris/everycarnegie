# everycarnegie — Bluesky profile

Everything needed to set the account up. Nothing here is posted automatically:
the account does not exist yet, and the pinned post is written by
`everycarnegie_post.py --pin` once it does, following everylibrary's pattern.

## Handle and name

| | |
|---|---|
| Handle | `everycarnegie.bsky.social` |
| Display name | **Every Carnegie Library** |
| Avatar | `avatar/avatar.png` (1024×1024, 40 KB) |

All three candidate handles were free when checked on 18 August 2026:
`everycarnegie`, `everycarnegielibrary`, `carnegielibraries`. ⚠️ Note that
`everylibrary.bsky.social` is **taken by an American library PAC**, so the
obvious name was never available.

The handle is short; the display name does the explaining. That is the same
split as Every U.K. Library, and it removes the one weakness of the short
form, which is that "Every Carnegie" alone could be read as every person of
that name.

## Description

221 characters. Every U.K. Library's is 185, for comparison.

```
A 🤖 visiting every library Andrew Carnegie paid for, 1883–1929, one at a time. Photos from Wikimedia Commons; image descriptions are A.I.-generated. Sources and credits in the pinned post. Run by @stanfordc.bsky.social. 📚
```

Three things about it are deliberate:

- **"Andrew Carnegie", not "Carnegie library".** The term is universal in
  library circles and not outside them, and "every library Andrew Carnegie paid
  for" explains the whole premise in six words.
- **The date range attaches to the grant, not to the bot.** As its own sentence
  it reads for a moment like the bot's own schedule.
- **"Sources and credits"**, matching the sibling bot. Not cosmetic: every
  photograph is CC BY-SA, CC BY, CC0 or public domain, so credit is a licence
  condition rather than a courtesy.

No "not affiliated with" line, unlike Every U.K. Library and KBO in English.
There is no Carnegie library service to be mistaken for.

## Pinned post

277 characters, within the 300 limit. Wikipedia's credit is a licence
requirement and not politeness: the "what became of it" line in every post is
Wikipedia's prose, lightly trimmed, so CC BY-SA covers the text as well as the
pictures. Bios carry no link facets, which is why the working links have to
live in a post at all.

```
Sources and credits 📚

Photographs: Wikimedia Commons contributors, credited by name on every post.

Libraries, grants and dates: Wikipedia's lists of Carnegie libraries (CC BY-SA).

1,850 of the 2,509 he built; the 660 in Britain and Ireland are not yet included.
```

Ireland's 56 rows are **held back** as of 18 August 2026, because they come
from a table with no library-name column, their names are streets rather than
libraries, and one entry is a lighthouse. Wikipedia counts Britain and Ireland
together as one bloc of 660, so the gap is a single clean sentence rather than
two caveats. Restore them by clearing `HELD_COUNTRIES` in `carnegie_images.py`
once they have been checked, and raise the figure here to match.

## Launch

29 August, the anniversary of Dunfermline Carnegie Library opening in 1883: the
first of the 2,509. Its foundation stone was laid on 27 July 1881 by Carnegie's
mother, Margaret, and the town declared a public holiday for the opening.

Carnegie's own birthday, 25 November 1835, was the obvious alternative and is
the weaker one. It makes the bot about the man rather than the buildings, and
the interesting thing here is the 1,900 towns that took his bargain: he paid
for the building, they supplied the land and committed to its upkeep.
