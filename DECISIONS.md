# everycarnegie — open decisions

Every choice still live, with **all** the options considered, including the ones
that were discarded and why. Decided items are at the bottom.

---

## 1. Launch post ⬜ OPEN

Five approaches were considered. Only the last three were shown before.

| | Approach | Why it was or wasn't put forward |
|---|---|---|
| 1 | **No launch post.** Just start the rotation on 29 August. | Discarded silently. The anniversary passes unremarked, which wastes the only date the bot will ever have. |
| 2 | **Announcement, no photograph.** Text-only post explaining what the bot is. | Discarded silently. Weakest option: the account is about buildings and its first post would show none. |
| 3 | **A thread**: the anniversary, then the first library. | Discarded silently. Threads read as launch marketing, and no other bot here does it. |
| 4 | **Start with a normal roster library**, no special post. | Discarded silently. Honest, but it throws away Dunfermline. |
| 5 | **Dunfermline as the first post.** ⭐ built | Shown, in three wordings below. |

### If Dunfermline: one post or a thread?

Rendered with the photograph at `data/launch_options.html`:

```bash
python3 launch_options_page.py && open data/launch_options.html
```

| | Structure | Lengths | |
|---|---|---|---|
| i | One post | 292 | Built. The bargain, the thing that makes these buildings interesting, does not appear at all. |
| ii | Two posts | 282 + 248 | Hook, then the bargain and one line on what the account does. |
| iii ⭐ | Three posts | 282 + 204 + 249 | Each post does one job: anniversary, bargain, what the account posts. |
| iv | Thread ending in the credits note, pinned | — | Would save duplicating the scope line. ⚠️ **Unverified whether Bluesky can pin a reply.** Check before the 29th. |

Threading was dismissed early as "reading like launch marketing". That was
wrong: this is a bot explaining a subject most people do not know, launch day
is the only day anyone reads a profile properly, and every post after it is a
single, so the thread sets no pattern it will not keep.

⚠️ Threading needs a code change. `post_launch` sends one post; replies need
root and parent refs threaded through, roughly fifteen lines.

⚠️ In option iii, post 3 overlaps the pinned post on scope. Either trim it to
what the account does and let the pinned post own the numbers, or accept the
repetition on day one.

### ⚠️ Post 2 of the thread is too vague, and here is the fix

As drafted it reads: *"Carnegie paid for the building. The town had to supply
the land and fund the running of it, every year, for good."* That states a deal
without stating its terms, so a reader cannot see why it matters.

The actual terms, verified from Wikipedia's Carnegie library article — the
"Carnegie formula" — are specific and much stronger:

- demonstrate the need for a public library
- provide the building site
- pay the staff and maintain it
- draw on **public funds**, not private donations
- **"annually provide ten percent of the cost of the library's construction to
  support its operation"**
- provide free service to all

So a town taking a $10,000 library was voting to spend $1,000 a year of its own
tax revenue, indefinitely. Some refused: in Canada in 1901 Carnegie offered
$2.5m for 125 libraries and *"most cities at first turned him down, then
eventually took the money."*

Rewritten with the terms named:

```
Carnegie paid for the building. To get one, a town had to provide the land and
commit ten percent of the build cost every year, out of public taxes, to run it.

2,508 towns took that deal. Some refused it.
```

That is the subtext made explicit: these are not gifts, they are contracts, and
every surviving Carnegie library is a town that voted to tax itself and kept
paying.

### The opening line, and the closing line

`"2,508 followed by 1929."` was ambiguous — it read as a sequence, 2,508 then
1929, rather than "2,508 more were built, finishing in 1929". Replaced with
`"By 1929 there were 2,509 of them."`, which also closes the loop the post
opens and matches the total used in the bio and the pinned post.

Openings costed against the 300 limit: "The first." (287) · **"The world's
first Carnegie library." (293, or 282 with a shorter closing line)** ⭐ · "The
first Carnegie library anywhere." (283) · "The first of the 2,509." (289,
duplicates the arithmetic) · "Where it all started." (282, different register
from every other post) · "The first library Andrew Carnegie ever paid for."
(295).

### The three wordings, as first drafted

**A — the holiday detail** (287 chars) ⭐ recommended, and built

```
Dunfermline, Fife 📚
Abbot Street

The first. It opened 143 years ago today, on 29 August 1883. Carnegie's mother had laid the foundation stone; the town declared a public holiday.

2,508 followed, over the next 46 years.

📷 Stephencdickson · CC BY-SA 3.0

#CarnegieLibraries #Dunfermline
```

**B — the bargain** (298 chars). Accurate: he emigrated in 1848, aged 12. Almost no slack under the limit.

```
Dunfermline, Fife 📚
Abbot Street

The first, opened 143 years ago today on 29 August 1883 in the town Carnegie left as a boy.

He paid for the building. The town supplied the land and its upkeep. 2,508 more followed on those terms.

📷 Stephencdickson · CC BY-SA 3.0

#CarnegieLibraries #Dunfermline
```

**C — plainest** (265 chars)

```
Dunfermline, Fife 📚
Abbot Street

The first Carnegie library, opened 143 years ago today on 29 August 1883. His mother laid the foundation stone and the town took a holiday.

2,508 followed by 1929.

📷 Stephencdickson · CC BY-SA 3.0

#CarnegieLibraries #Dunfermline
```

⚠️ Whichever is chosen, Dunfermline is **not in the roster** — Britain is held
back — so the row is hardcoded in `everycarnegie_post.py` as a deliberate
one-off.

---

## 2. Pinned post wording ⬜ OPEN

**A** (264 chars) ⭐ recommended, and what `--pin` currently builds

```
Sources and credits 📚

Photographs: Wikimedia Commons contributors, credited by name on every post.

Libraries, grants and dates: Wikipedia's lists of Carnegie libraries (CC BY-SA).

1,850 of the 2,509 he built; the 660 in Britain and Ireland are not yet included.
```

**B — terser, no gap named** (243 chars). Drops the completeness claim entirely.

```
Sources and credits 📚

Photographs: Wikimedia Commons contributors, credited by name on every post.

Grants, dates and notes: Wikipedia's lists of Carnegie libraries (CC BY-SA).

Covers 1,910 of the 2,509 built; Britain's are not yet included.
```

**C — points at a reply for detail** (248 chars). Needs a second post written.

```
Sources and credits 📚

Photographs: Wikimedia Commons contributors, credited by name on every post.

Grants, dates and notes: Wikipedia's lists of Carnegie libraries (CC BY-SA).

Image descriptions are A.I.-written. Not yet complete: see the reply.
```

## 3. Where the pinned post's Wikipedia link points ⬜ OPEN

| | Target | Trade |
|---|---|---|
| a ⭐ | `List_of_Carnegie_libraries_in_the_United_States` | Where most of the data came from; under-sells the other 15 countries. Current behaviour. |
| b | `Carnegie_library` | Covers the whole programme; is not the source of the data. |
| c | Both, as two links | Truthful, but three links in one short post. |

## 4. Cadence ⬜ OPEN — nothing is scheduled yet

1,223 postable today.

| Rate | Runs for | Note |
|---|---|---|
| 1/day | 3 yr 4 mo | Matches "The Daily Carnegie" idea you set aside |
| 2/day | 1 yr 8 mo | |
| 3/day ⭐ | 1 yr 1 mo | Matches everylibrary's rhythm |

Also open: what times. everylibrary posts at 17:00, 21:00 and 01:00 Seoul,
chosen to land at 09:00, 13:00 and 17:00 UK. This corpus is 88% American, so
US times may suit it better.

## 5. The thin posts ⬜ OPEN — you have not ruled

19 rows have no grant, no date and no note, so the post is a place, a
photograph and a credit. Recommended: post them, the picture is the content.
Alternatives: hold them back, or write a fallback line.

## 6. Ireland ✅ DECIDED — held back

56 rows, 18 postable. Restore by clearing `HELD_COUNTRIES` in
`carnegie_images.py`.

## 7. Name and bio ✅ DECIDED

`everycarnegie.bsky.social`, display "Every Carnegie Library", bio D as edited
by you. See `PROFILE.md`.

## 8. Launch date ✅ DECIDED — 29 August

Anniversary of Dunfermline opening, 1883. Alternatives were 25 November
(Carnegie's birth), 11 August (his death), 27 July (foundation stone).
