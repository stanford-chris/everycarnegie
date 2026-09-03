#!/usr/bin/env python3
"""
launch_thread_stress.py — the hostile version of the opening thread, and what
it exposes in the real one.

Nothing here is meant to be posted. It exists to answer one question: if
somebody set out to write the opposite thread, what would they use, and does
any of it land on ground the real thread has left open?

Everything the cynic says is drawn from the same two Wikipedia articles the
launch thread is sourced from — Carnegie library and Andrew Carnegie, checked
19 August 2026 — because an attack built from the bot's own sources is the only
kind worth defending against.

⚠️ **This page has now raised three findings and all three are closed.**

The first was that the exposure was not an omission but a euphemism: "when the
steel money came", in the old post 3, the one clause the bot wrote in its own
voice about where the money came from. Cutting the thread from seven posts to
two deleted the post it lived in.

The second was that the cut left "and gave away about 90 percent of his wealth"
standing with nothing on the other side of it, so four sentences read as his own
case for himself. That line was cut on 19 August 2026. Both times the fix went
in the direction of saying less about the man, and the second cut removed a
flattering claim, not an unflattering one.

The third was the account's own name. It is called "every" and the roster holds
1,910 of 2,509, so a reader who worked the arithmetic out before reaching the
pinned post found a discrepancy where they could have had a disclosure. Post 2
now says it: "though Britain's 660 are not in it yet".

What is left is omission, which a two-post launch claiming no completeness can
defend. The two remaining items in the table are jobs for the roster and the
daily posts rather than for launch day.

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
    ("“and gave away about 90 percent of his wealth”",
     "✅ Cut 19 August 2026.",
     "resolved",
     "The finding of the previous run, and the second one in a row that the edits have "
     "closed. It was true and it was sourced; what made it a liability was that at two "
     "posts nothing stood on the other side of it, so the thread read as his own case for "
     "himself. It is the rare cut that goes in the flattering direction."),

    ("“when the steel money came”",
     "✅ Gone with the seven-post version.",
     "resolved",
     "The original finding: omission is editing, but a euphemism is a voice. Simplifying "
     "for neutrality deleted the post it lived in."),

    ("The account itself: “every”, when the roster is 1,910 of 2,509",
     "✅ Said in post 2 from 19 August 2026.",
     "resolved",
     "Third finding, third close. “Every” is in the account’s name, so a reader who works "
     "the arithmetic out before reaching the pinned post would have found a discrepancy "
     "where they can now find a disclosure. 265 of 300."),

    ("The account itself: a feed of handsome buildings",
     "Post 2 states what it posts, neutrally.",
     "medium",
     "The closing line of the cynic’s thread, and the one charge a neutral launch cannot "
     "answer on launch day, because the answer is what the daily posts turn out to "
     "contain. Nothing to do here; it is a standing obligation on the roster."),

    ("Homestead, 1892: ten dead, and the Homestead library owned by Carnegie Steel",
     "Not mentioned.",
     "low",
     "Downgraded by the cut above. While post 1 characterized the man, its silence on "
     "Homestead was selective; now the thread says only what he was and what he paid for, "
     "and a launch that plainly does not attempt a biography is not concealing one."),

    ("Carnegie’s own “better cut of meat” answer to workers who wanted wages",
     "Not mentioned.",
     "low",
     "The most quotable thing in the story, and out of scope for two posts."),

    ("Buildings only: no books, no salaries. The ten percent, in perpetuity",
     "Not mentioned. The old post 4 carried it.",
     "low",
     "The most interesting thing about these buildings and the least accusatory: a "
     "contract, not a charge. The one candidate worth restoring if the thread ever goes "
     "to three posts."),

    ("Segregation, and grants sized on the white population",
     "Not mentioned. The old post 5 carried it squarely.",
     "medium",
     "⚠️ A decision, not a finding, and the one item on this page that does not shrink "
     "with the thread. Defensible in a launch claiming no completeness. It stops being "
     "defensible the moment the account posts one of the segregated libraries without "
     "saying so, which is a job for the daily posts and the roster."),
]

# ------------------------------------------------------------- what to do

OPTIONS = [
    ("1", "Post it as it now stands.", "recommended",
     "Two posts. All three findings this page has raised are closed, and the thread now "
     "states what he was, what he paid for, what the account will post and what it does "
     "not yet cover, with no verdict on anybody. What is left is omission, which a launch "
     "claiming no completeness can defend, and the two remaining items are jobs for the "
     "roster and the daily posts rather than for 29 August."),

    ("2", "Restore the terms as a third post.", "live",
     "The ten percent, in perpetuity, out of public taxes. A contract rather than a "
     "charge, and the thing most readers do not know. ⚠️ It reopens the length question "
     "that the cut settled."),

    ("3", "Put the harder material in the pinned post instead.", "rejected",
     "The pinned post already carries the roster gap and the sources. Rejected for the "
     "rest: doing quietly what the thread declined to do out loud is worse than either "
     "doing it or not."),

    ("4", "Go back to seven posts.", "rejected",
     "Recorded so the ground is not re-covered. It was a good thread and it is in "
     "`git log`. Neutrality was the instruction, and five of those posts existed to "
     "characterize the man."),

    ("5", "Restore the 90 percent line.", "rejected",
     "⚠️ Recorded because it is the obvious thing to reach for if the thread ever looks "
     "thin. It is true and sourced. It went because at two posts nothing balances it, so "
     "restoring it without restoring something to pull the other way puts the finding "
     "straight back."),
]

# --------------------------------------------------------------- rewrites

_P1 = REAL[0][0]
_P2 = REAL[1][0]

REWRITES = [
    ("Post 1, as it now stands", _P1,
     "61 characters spare. States what he was, and nothing about what to make of it."),

    ("Post 1, as it was until 19 August", _P1.replace(
        "Andrew Carnegie was born here in 1835, and later became the richest man in the world.",
        "Andrew Carnegie was born here in 1835. He later became the richest man in the world, "
        "and gave away about 90 percent of his wealth."),
     "284 chars. Kept here so the cut is visible rather than remembered."),

    ("Post 2, as it now stands", _P2,
     "35 characters spare, with the roster gap as its own closing sentence."),

    ("Post 2, before the roster gap went in", _P2.replace(
        " Britain’s 660 are not included yet.", ""),
     "229 chars. The pinned post carried the admission alone until 19 August."),

    ("Post 2, the broken first attempt at it", _P2.replace(
        "This account posts them one at a time:", "This account posts them one at a time, "
        "though Britain’s 660 are not in it yet:").replace(
        " Britain’s 660 are not included yet.", ""),
     "⚠️ “not in it yet” had no antecedent, and collided with the “it” four words later "
     "that means the building. Kept as the reason the disclosure is a separate sentence."),
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
.lede{margin:0 0 22px;font-size:15.5px}
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
.resolved{background:var(--ok);color:#fff}
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
    doc = [f'<meta charset="utf-8">'
           f"<title>Carnegie — the cynical thread</title><style>{CSS}</style>",
           "<div class=wrap>",
           "<h1>The opposite thread, and what it lands on</h1>",
           "<p class=sub>Every fact and every quotation below is from the two Wikipedia "
           "articles the launch thread is sourced from, checked 19 August 2026. An attack "
           "built from the bot’s own sources is the only kind worth defending against.</p>",

           "<p class=lede>Nothing here is for posting. <b>Three findings raised, all "
           "three closed.</b> “When the steel money came” went with the seven-post version; "
           "“and gave away about 90 percent of his wealth” was cut on 19 August; and post 2 "
           "now says the roster gap out loud rather than leaving it to the pinned post. The "
           "first two fixes went the same way, towards saying less about the man, and the "
           "second removed a flattering claim rather than an unflattering one. What is left "
           "is omission, which a launch claiming no completeness can defend.</p>",

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

           "<h2>1 · The real thread, as it now stands</h2>",
           "<p class=sub>Two posts, 239 and 265 of 300. Nothing is marked: no sentence "
           "in it is now in the account’s own editorial voice.</p>",
           thread_html(real),

           "<h2>2 · The cynic’s thread</h2>",
           "<p class=sub>Seven posts, same anniversary, hostile author. Left at seven "
           "deliberately: the question is what an attacker has available, not what they "
           "would have room for.</p>",
           thread_html(CYNIC),

           "<h2>3 · Where the real thread stands</h2>",
           "<table><tr><th>The charge</th><th>Exposure</th><th>What the thread says, "
           "and what it costs</th></tr>"]

    for charge, stands, level, note in EXPOSURE:
        doc.append(f"<tr><td><b>{charge}</b></td>"
                   f"<td><span class='pill {level}'>{level}</span></td>"
                   f"<td>{stands}<br><span style='color:var(--muted)'>{note}</span></td></tr>")
    doc.append("</table>")

    doc += ["<h2>4 · Every option, including the ones not worth taking</h2>"]
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
