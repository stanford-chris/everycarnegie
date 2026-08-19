#!/usr/bin/env python3
"""
launch_thread_stress.py — the hostile version of the opening thread, and what
it exposes in the real one.

Nothing here is meant to be posted. It exists to answer one question: if
somebody set out to write the opposite thread, what would they use, and does
any of it land on ground the real thread has left open?

Everything the cynic says is drawn from the same two Wikipedia articles the
launch thread is already sourced from — Carnegie library and Andrew Carnegie,
checked 19 August 2026 — because an attack built from the bot's own sources is
the only kind worth defending against. The quotations are the articles' own:
Carnegie on the better cut of meat, Richard White on leisure, the Corporation
sizing grants on the white population, Twain on buying fame.

⚠️ The finding: the thread's exposure is not what it omits. Homestead, the
better-cut-of-meat quote and the books-not-buildings gap are all missing, but
omission is a fair editorial choice in seven posts. The exposure is one clause
the bot writes in its own voice — "when the steel money came" — which is the
single place in the thread where it puts a thumb on the scale.

Usage:
    python3 launch_thread_stress.py     # writes data/launch_thread_stress.html
"""

import html
from pathlib import Path

from launch_thread import POSTS as REAL

# ---------------------------------------------------------------- the cynic

CYNIC = [
    """Dunfermline, Scotland 📚

Andrew Carnegie was born here in 1835. He became the richest man in the world by buying out his partners and holding his workers’ wages down, then gave the money back to their towns as buildings the towns had to staff, heat and fill themselves.""",

    """In 1892 his partner Frick cut wages at the Homestead mill by up to 22% and locked the men out. Pinkerton agents came up the river on barges. Seven strikers and three Pinkertons were killed.

Carnegie had left for Scotland before it broke.""",

    """The libraries at Homestead, Braddock and Duquesne were not the towns’. They were owned by Carnegie Steel.

Richard White: he “imposed work rules that deprived his employees of virtually all their leisure; then he built a library and lectured them on how to spend time they did not have.”""",

    """His men said they would rather have the wages. He answered:

“If I had raised your wages, you would have spent that money by buying a better cut of meat or more drink for your dinner. But what you needed, though you didn’t know it, was my libraries and concert halls.”""",

    """The grants bought the building and nothing in it. No books, no salaries.

To qualify, a town handed over the land and committed 10% of the build cost every year, for good, out of local taxes. Plenty of small towns took a monument they then could not afford to run.""",

    """In the segregated South he did not make existing libraries admit Black readers. He paid for separate ones.

The Carnegie Corporation told communities to size their grants on the white population alone. Du Bois fought that in Atlanta in 1902.""",

    """Mark Twain thought he used philanthropy to buy fame.

He bought 2,509 buildings’ worth of it, and now an account that will post a handsome photograph of each one in turn.""",
]

# ⚠️ The cynic's last post first read "2,509 buildings with his name over the
# door". That is the kind of line the discipline of this page exists to catch:
# it sounds unanswerable and the article says the opposite — "No architectural
# style was recommended for the exterior, nor was it necessary to put Andrew
# Carnegie's name on the building." Many do carry it, but not by requirement,
# so the sentence would have been the one thing in the hostile thread that
# could be knocked down. Cut rather than kept, because a cynic who overreaches
# is not the cynic worth preparing for.

# ---------------------------------------------- where the real thread stands

EXPOSURE = [
    ("Carnegie’s own “better cut of meat” answer to workers who wanted wages",
     "Not mentioned.",
     "medium",
     "The most quotable thing in the whole story and it is in the bot’s own source. Leaving it out is defensible; being seen to leave it out is the risk, because anyone who looks it up finds it in the first article."),

    ("Homestead, 1892: ten dead, and the Homestead library owned by Carnegie Steel",
     "Not mentioned.",
     "high",
     "This is the one a hostile reply will actually use, and it is one search away. The thread spends post 3 on the origin story instead."),

    ("“when the steel money came”",
     "Post 3, the bot’s own wording.",
     "high",
     "⚠️ The real exposure. Everything else is omission, which is editing. This is a euphemism the bot wrote itself: money that “came”, from nowhere, to be spent well. One clause, and it is the only place in seven posts where the account sounds like a fan."),

    ("“gave away about 90% of his wealth”",
     "Post 1, unqualified.",
     "medium",
     "True and sourced, but it is the sentence a critic quotes back as the bot doing his public relations. It sits in the same breath as “richest man in the world” with nothing between them about how."),

    ("Buildings only: no books, no salaries",
     "Half covered. Post 4 says the town paid staff and 10% a year.",
     "low",
     "Post 4 already makes the deal sound hard. Adding “and no books” sharpens it at almost no cost."),

    ("Towns lumbered with upkeep they could not meet",
     "Post 4 implies it; post 6 says some buildings were converted or lost.",
     "low",
     "Adequately covered between the two."),

    ("Segregation, and grants sized on the white population",
     "Post 5, squarely.",
     "low",
     "Already the strongest post in the thread. The Corporation’s appropriation rule and Du Bois in Atlanta would harden it further if there were room."),

    ("Paternalism: libraries as social control",
     "Not mentioned.",
     "low",
     "Post 4’s terms carry the flavour without the argument. A thread cannot hold everything."),

    ("The account itself: “every”, when the roster is 1,910 of 2,509",
     "Post 7 does not say it; the pinned post does.",
     "medium",
     "Cheap to fix and awkward if a reader finds the gap before the pinned post does. The bio does not carry it either."),

    ("The account itself: a feed of handsome buildings",
     "Post 7 states what it posts, neutrally.",
     "medium",
     "The closing line of the cynic’s thread. There is no answer to it except the thread having already said the unflattering part out loud, which is the argument for fixing post 3 rather than post 7."),
]

# ------------------------------------------------------------- what to do

OPTIONS = [
    ("1", "Change nothing.", "rejected",
     "Defensible: posts 4 and 5 already carry the terms and the segregation, which is more than most heritage accounts manage. Rejected on one point only — post 3’s wording is the bot’s own, not an omission, so “we chose not to cover it” is not available as a defence."),

    ("2", "Fix the wording of post 3, change nothing else.", "live",
     "The minimal change that answers the actual exposure. Ten words. Keeps the thread at seven posts and keeps the origin story intact."),

    ("3", "Replace post 3 with Homestead and the quote.", "recommended",
     "Spends the thread’s softest post on its hardest fact. Still seven posts. The origin story survives in post 2; what is lost is the sentence that ties it to the libraries, which post 4 partly does anyway."),

    ("4", "Keep post 3, add an eighth post on Homestead.", "live",
     "Loses nothing, and eight is not too long for a launch. Costs the thread its shape: post 4’s “They were not gifts, though” reads as the turn, and putting the turn one post earlier blunts it."),

    ("5", "Reorder: the money first, the boy and the books after.", "rejected",
     "Answers the criticism structurally rather than by addition. Rejected because it throws away the anniversary opening: post 1 exists to say “this building, 143 years ago today”, and a thread that opens on Pinkertons on barges is a different account."),

    ("6", "Leave launch day alone; post the Homestead thread separately later.", "live",
     "Arguably the better journalism: one subject per thread, and it gives the account something to say on 6 July. ⚠️ It also means the first thing anyone reads is the uncomplicated version, which is exactly the charge."),

    ("7", "Put the caveat in the pinned post or the bio instead.", "rejected",
     "The pinned post already carries the roster gap. Rejected for the rest: nobody reads a bio for a moral position, and it would be doing quietly what the thread declined to do out loud."),
]

# --------------------------------------------------------------- rewrites

REWRITES = [
    ("Post 3, as written", REAL[2][0], "The two exposed words are in the second clause."),

    ("Post 3, option 2 — wording only",
     """Carnegie credited that library with his start. Forty years later, with a fortune made from other men’s twelve-hour days in his steel mills, he began buying the same thing for their towns.""",
     "Names where the money came from without leaving the origin story. ⚠️ “twelve-hour days” is not in either Wikipedia article — verify it before posting, or cut to “made in his steel mills”."),

    ("Post 3, option 3 — Homestead instead",
     """In 1892 his partner Frick cut wages at the Homestead mill and locked the men out. Ten died. Carnegie was in Scotland.

The library he built there was owned by the steel company, not the town. Asked why not wages, he said his men needed his libraries, though they didn’t know it.""",
     "Every clause is in the Andrew Carnegie or Carnegie library articles. 279 characters."),

    ("Post 4, sharpened by four words",
     """They were not gifts, though.

To get one, a town had to provide the land, pay the staff, keep it free to everyone and commit 10% of the building’s cost every year, out of public taxes, to run it. He paid for the building. Not the books.""",
     "“Not the books” is the fact most people do not know and it costs nothing."),

    ("Post 7, closing the roster gap",
     """This account posts them one at a time: the building and what became of it, what Carnegie paid and what that money is worth now. Britain’s 660 are not in it yet.

Photos: Wikimedia Commons contributors, credited on every post. Image descriptions are A.I.-written.""",
     "Takes the pinned post’s admission and says it where the readers are."),
]


CSS = """
:root{color-scheme:light dark;--bg:#faf9f7;--card:#fff;--ink:#1a262b;--muted:#5d6b70;
      --line:#e3e0da;--warn:#a33;--ok:#2c6e49;--flag:#8a6d1f}
@media (prefers-color-scheme:dark){:root{--bg:#14191c;--card:#1c2429;--ink:#e8ddc8;
      --muted:#9aa8ad;--line:#2b353a;--warn:#e08b8b;--ok:#7fbf9a;--flag:#d9bd6a}}
*{box-sizing:border-box}
body{margin:0;padding:38px 22px 100px;background:var(--bg);color:var(--ink);
     font:16.5px/1.58 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.wrap{max-width:760px;margin:0 auto}
h1{font-size:25px;margin:0 0 8px}
h2{font-size:19px;margin:46px 0 6px;padding-top:22px;border-top:1px solid var(--line)}
.sub{color:var(--muted);font-size:14.5px;margin:0 0 6px}
.lede{margin:0 0 22px;color:var(--muted);font-size:15px}
.src{background:var(--card);border:1px solid var(--line);border-radius:12px;
     padding:13px 15px;font-size:13.5px;color:var(--muted);margin:0 0 8px;line-height:1.5}
.src a{color:inherit}
.thread{border-left:2px solid var(--line);padding-left:16px;margin-top:18px}
.post{background:var(--card);border:1px solid var(--line);border-radius:14px;
      padding:15px 17px 10px;margin:0 0 12px}
.post.hot{border-color:var(--warn)}
.text{white-space:pre-wrap;margin:0 0 8px}
.meta{color:var(--muted);font-size:12px}
table{border-collapse:collapse;width:100%;margin-top:14px;font-size:14.5px}
th,td{text-align:left;vertical-align:top;padding:9px 10px;border-bottom:1px solid var(--line)}
th{font-size:12.5px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
.pill{font-size:11.5px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;
      padding:2px 8px;border-radius:99px;white-space:nowrap;display:inline-block}
.high{background:var(--warn);color:#fff}
.medium{background:var(--flag);color:#fff}
.low{background:var(--line);color:var(--muted)}
.recommended{background:var(--ok);color:#fff}
.rejected{background:var(--line);color:var(--muted)}
.live{background:var(--flag);color:#fff}
.opt{background:var(--card);border:1px solid var(--line);border-radius:14px;
     padding:14px 16px;margin:0 0 11px}
.opt h3{font-size:16px;margin:0 0 6px;display:flex;gap:9px;align-items:center}
.opt p{margin:0;color:var(--muted);font-size:14.5px}
.rw{background:var(--card);border:1px solid var(--line);border-radius:14px;
    padding:15px 17px;margin:0 0 13px}
.rw h3{font-size:15px;margin:0 0 9px}
.rw .text{background:transparent;font-size:15.5px}
.rw .note{color:var(--muted);font-size:13.5px;margin:9px 0 0;padding-left:11px;
          border-left:2px solid var(--line)}
"""


def thread_html(posts, hot=()):
    out = ['<div class=thread>']
    for i, t in enumerate(posts, 1):
        cls = "post hot" if i in hot else "post"
        over = "  ⚠️ OVER 300" if len(t) > 300 else ""
        out.append(f'<div class="{cls}"><p class=text>{html.escape(t)}</p>'
                   f'<p class=meta>{i}/{len(posts)} · {len(t)} chars{over}</p></div>')
    out.append('</div>')
    return "\n".join(out)


def main():
    real = [t for t, _ in REAL]
    doc = [f"<title>Carnegie — the cynical thread</title><style>{CSS}</style>",
           "<div class=wrap>",
           "<h1>The opposite thread, and what it lands on</h1>",
           "<p class=sub>Every fact and every quotation below is from the two Wikipedia "
           "articles the launch thread is already sourced from, checked 19 August 2026. "
           "An attack built from the bot’s own sources is the only kind worth defending "
           "against.</p>",
           "<p class=lede>Nothing here is for posting. The finding is at the foot of the "
           "table: the thread’s weak point is not what it leaves out, it is one clause "
           "it wrote itself.</p>",

           "<p class=src><b>The two sources, and nothing else:</b><br>"
           "<a href='https://en.wikipedia.org/wiki/Carnegie_library'>"
           "en.wikipedia.org/wiki/Carnegie_library</a> — the “better cut of meat” answer, "
           "the company-owned libraries at Homestead, Braddock and Duquesne, buildings but "
           "no books, the ten percent, grants sized on the white population, Du Bois in "
           "Atlanta in 1902, Twain on buying fame, the staircase and the lamp post.<br>"
           "<a href='https://en.wikipedia.org/wiki/Andrew_Carnegie'>"
           "en.wikipedia.org/wiki/Andrew_Carnegie</a> — Frick’s 22% cut and the lockout, "
           "the Pinkerton barges, seven strikers and three Pinkertons dead, Carnegie "
           "leaving for Scotland before it broke, and Richard White on leisure.</p>",

           "<h2>1 · The cynic’s thread</h2>",
           "<p class=sub>Same seven posts, same anniversary, hostile author.</p>",
           thread_html(CYNIC),

           "<h2>2 · Where the real thread stands</h2>",
           "<table><tr><th>The charge</th><th>Exposure</th><th>What the thread says, "
           "and what it costs</th></tr>"]

    for charge, stands, level, note in EXPOSURE:
        doc.append(f"<tr><td><b>{charge}</b></td>"
                   f"<td><span class='pill {level}'>{level}</span></td>"
                   f"<td>{stands}<br><span style='color:var(--muted)'>{note}</span></td></tr>")
    doc.append("</table>")

    doc += ["<h2>3 · The real thread, with the exposed post marked</h2>",
            thread_html(real, hot=(3,)),

            "<h2>4 · Every option, including the ones not worth taking</h2>"]
    for num, title, status, why in OPTIONS:
        doc.append(f"<div class=opt><h3>{num}. {html.escape(title)} "
                   f"<span class='pill {status}'>{status}</span></h3><p>{why}</p></div>")

    doc += ["<h2>5 · The rewrites in full</h2>"]
    for title, text, note in REWRITES:
        over = "  ⚠️ OVER 300" if len(text) > 300 else ""
        doc.append(f"<div class=rw><h3>{html.escape(title)} "
                   f"<span class=meta>· {len(text)} chars{over}</span></h3>"
                   f"<p class=text>{html.escape(text)}</p>"
                   f"<p class=note>{note}</p></div>")

    doc.append("</div>")

    out = Path(__file__).resolve().parent / "data" / "launch_thread_stress.html"
    out.write_text("\n".join(doc), encoding="utf-8")
    print(f"wrote {out}")
    for title, text, _ in REWRITES:
        flag = "  ⚠️ OVER" if len(text) > 300 else ""
        print(f"  {len(text):>4} chars  {title}{flag}")


if __name__ == "__main__":
    main()
