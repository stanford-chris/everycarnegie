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

## 9. Avatar ✅ DECIDED 19 August 2026 — keep A, the night facade with the lit lamp

Eight approaches were drawn and judged at 40 px, the size that decides it.
Regenerate the sheet with `python3 avatar/make_avatar_options.py`.

| | Approach | Why it was or wasn't taken |
|---|---|---|
| **A** ⭐ | **Night facade, lit lamp post** | **Kept.** Reads at 40 px, and both of its motifs are documented. |
| B | The lamp alone | Survives 40 px well, and the enlightenment lantern is the one motif Carnegie's office attached a meaning to. Says "light", not "library". |
| C | The same facade by day, ink on limestone | The strongest alternative: inverting the ground is the biggest change available at thumbnail size. Rejected as a colourway, not a new idea. |
| D | The carved lintel, "CARNEGIE LIBRARY" | ⚠️ Illegible at 40 px, **and wrong**: the article says it "was not necessary to put Andrew Carnegie's name on the building". |
| E | A date stamp, built like everylibrary's | Ring text turns to mush at 40 px, exactly as it does on the sibling. Its backstory is a British library book's return slip, and this corpus is 88% American. |
| F | The lit doorway, light falling down the steps | Runner-up, and the only candidate that says something new: the entrance staircase is also the standing criticism of these buildings. |
| G | The steps alone | Reads as a stack of bars. Elevation by learning with the learning removed. |
| H | The arched fanlight | Fills the circular crop better than anything else, but fanlights are not mentioned in the article at all. |

⚠️ **The provenance split is the useful finding, and it applies to A as well.**
The entry staircase ("symbolized a person's elevation by learning") and the
entrance lamp post ("meant as a symbol of enlightenment") are Wikipedia's. The
temple front is not: no style was recommended, and each town chose its own, from
Beaux-Arts to Scottish Baronial. The colonnade is what we picture, not what he
specified. That is a fair thing for an avatar to do and a bad thing for a post
to do, so it is written down here rather than left to be rediscovered.

## 10. The opening thread ✅ DECIDED 19 August 2026 — two posts, neutral

Seven posts became two. What went: the foundation stone and the boy borrowing
books in Pittsburgh; his crediting that library with his start; the terms of the
deal; the segregated South and Savannah in 1914; and the counts, with about 900
of the US buildings still libraries by the 1990s. All in `git log`.

Two things were added back, because the draft dropped both and neither is taste:

- **The place header.** Post 1 opens "born here in 1835". Without
  "Dunfermline, Scotland" above it, "here" points at nothing but the photograph.
  It was absent from the seven-post version for arithmetic: naming the town in
  the prose and again in a header ran the post to 315. At two posts there is
  room, so the 📚 place format now starts on post 1 rather than with the dailies.
- **The photograph's credit.** The Dunfermline image is CC BY-SA 3.0, so
  attribution is a licence condition. Post 2's "credited on every post" is also
  a promise post 1 has to keep. 284 of 300 with it.

## 11. What the short thread is exposed to ✅ DECIDED 19 August 2026

`python3 launch_thread_stress.py` writes the opposite thread from the same two
Wikipedia articles the real one cites, and maps what it lands on. It has raised
three findings and **all three are now closed**.

1. **"when the steel money came"**, the old post 3: the one clause the bot wrote
   in its own voice about where the money came from, and the only line that
   could not be defended as an editorial choice. Cutting seven posts to two
   deleted the post it lived in.
2. **"and gave away about 90 percent of his wealth"**, post 1. Cut. In seven
   posts the terms of the deal and the segregation pulled against it; in two it
   stood alone, and the thread read: richest man in the world, gave away 90%,
   paid for 2,500 libraries. His own case for himself, made by an account nobody
   asked. ⚠️ **It was cut for being flattering, not for being wrong** — it is
   true and it is in the source. Post 1 is now 239 of 300 and says what he was
   and what he paid for, with no view on either.
3. **The account's own name.** It is called "every" and the roster holds 1,910
   of 2,509. Post 2 now says so: *"This account posts them one at a time, though
   Britain's 660 are not in it yet: …"* (269). A reader who worked the
   arithmetic out before reaching the pinned post found a discrepancy where they
   can now find a disclosure. ⚠️ **Raise the figure in post 2 if Britain is ever
   added**, or the disclosure becomes the inaccuracy.

⚠️ **Do not restore that line without restoring something to balance it.** It is
the obvious thing to reach for if the thread ever looks thin, and putting it back
alone puts the finding straight back.

What remains is omission, which a two-post launch claiming no completeness can
defend. Two things are still live, neither of them for launch day:

| | | |
|---|---|---|
| Segregation | ⚠️ tripwire | Defensible to omit from a launch claiming no completeness. **It stops being defensible the moment the account posts one of the segregated libraries without saying so.** A job for the daily posts and the roster. |
| "A feed of handsome buildings" | no action | The cynic's closing line, and the one charge a neutral launch cannot answer on launch day, because the answer is what the daily posts turn out to contain. |

Rejected and recorded so the ground is not re-covered: going back to seven posts
(neutrality was the instruction, and five of those posts existed to characterise
the man); putting the harder material in the pinned post instead (doing quietly
what the thread declined to do out loud is worse than either doing it or not);
restoring the terms of the deal as a third post (a contract rather than a
charge, and the best of the cut five, but it reopens the length question).
