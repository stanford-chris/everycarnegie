#!/usr/bin/env python3
"""
launch_thread.py — the opening thread for 29 August, and a page to read it on.

Two posts: what the building is, and what the account does. Neutral by
decision, 19 August 2026.

⚠️ It was seven posts until then, and the five that went are worth knowing
about, because losing them was the point rather than an accident. They were:
Carnegie's mother laying the foundation stone and the boy borrowing books in
Pittsburgh; his crediting that library with his start; the terms of the deal,
land plus ten percent of the build cost every year out of public taxes; the
segregated South and the separate libraries at places like Savannah in 1914;
and the counts, with about 900 of the US buildings still libraries by the
1990s. `git log` has them in full, as does DECISIONS.md item 10.

The last two lines of the short version are the load-bearing ones, and both
were absent from the draft this was cut down from:

⚠️ **The place header is not decoration here.** Post 1 opens "born here in
1835", and without "Dunfermline, Scotland" above it, "here" points at nothing
but the photograph. In the seven-post version the header was dropped for
arithmetic, because naming the town in the prose and again in a header ran the
post to 315 characters. The short version has the room, so the header comes
back and the 📚 place format now starts on post 1 rather than with the daily
posts.

⚠️ **The photograph's own credit is a licence condition, not a courtesy.** The
Dunfermline image is CC BY-SA 3.0, so "Photos: Wikimedia Commons contributors,
credited on every post" in post 2 is a promise post 1 has to keep by naming
Stephencdickson.

⚠️ **Post 2 says the roster gap out loud, and that is deliberate**, added 19
August 2026. It is a separate sentence at the end, and it has to stay one. The
first attempt folded it into the main clause — "posts them one at a time, though
Britain's 660 are not in it yet: the building and what became of it" — where
"it" had no antecedent at all, and collided with the "it" four words later that
means the building. The sentence's spine runs from "posts them" to the colon,
so nothing can sit between them. The account is called "every" and the roster holds 1,910 of the
2,509, almost all of the shortfall being the 660 in Britain and Ireland that
Wikipedia's lists carry as prose bullets rather than tables. The pinned post
already admits it, but a reader who works the arithmetic out before reaching
the pinned post finds a discrepancy where they could have had a disclosure.
Raise the figure here if Britain is ever added: see README.md.

⚠️ **"and gave away about 90 percent of his wealth" was cut on 19 August 2026,
and it was cut for being flattering rather than for being wrong.** It is true
and it is in the source. The reason it went is that at two posts it no longer
had anything on the other side of it: born here, richest man in the world, gave
away 90%, paid for 2,500 libraries reads as his own case for himself, made by
an account nobody asked. Everything else the short thread leaves out is an
omission it can defend; that was a positive claim it chose to include. What
remains states what he was and what he paid for, and holds no view on either.
Do not restore it without restoring something to balance it.

Every remaining claim is from the Andrew Carnegie and Carnegie library articles
on Wikipedia, checked 18 August 2026: born Dunfermline 1835; richest man in the
world; 2,509 buildings 1883-1929, which the post rounds to "more than 2,500";
Dunfermline first, opened 29 August 1883.

Usage:
    python3 launch_thread.py          # print the thread, render the page
    open data/launch_thread.html
"""

CREDIT = "\n\n📷 Stephencdickson · CC BY-SA 3.0"

# (text, carries_the_photograph)
POSTS = [
 ("""Dunfermline, Scotland 📚

Andrew Carnegie was born here in 1835, and later became the richest man in the world.

He paid for more than 2,500 public libraries. This was the first, opened 143 years ago today.""" + CREDIT, True),

 ("""This account posts them one at a time: the building and what became of it, what Carnegie paid and what that money is worth now. Britain’s are thin: Wikipedia lists barely a third of its 660.

Photos: Wikimedia Commons contributors, credited on every post. Image descriptions are A.I.-written.""", False),
]

IMAGE_TITLE = "File:The world's first Carnegie Library, in Dunfermline.JPG"
ALT = ("Pale stone building with rows of large rectangular windows and a prominent corner "
       "tower adorned with turrets and ornamental spires. Motorcycles parked at street level; "
       "clear skies with light cloud cover.")

if __name__ == "__main__":
    import html, urllib.parse
    from pathlib import Path

    over = [i for i, (t, _) in enumerate(POSTS, 1) if len(t) > 300]
    for i, (t, _) in enumerate(POSTS, 1):
        print(f"--- {i}/{len(POSTS)}  [{len(t)} chars]{'  ⚠️ OVER' if len(t) > 300 else ''}")
        print(t + "\n")
    print(f"{len(POSTS)} posts, longest {max(len(t) for t, _ in POSTS)}, over the limit: {over or 'none'}")

    img = ("https://commons.wikimedia.org/wiki/Special:FilePath/"
           + urllib.parse.quote(IMAGE_TITLE.replace("File:", "").replace(" ", "_")) + "?width=1000")
    css = """
:root{color-scheme:light dark;--bg:#faf9f7;--card:#fff;--ink:#1a262b;--muted:#5d6b70;--line:#e3e0da}
@media (prefers-color-scheme:dark){:root{--bg:#14191c;--card:#1c2429;--ink:#e8ddc8;--muted:#9aa8ad;--line:#2b353a}}
*{box-sizing:border-box}
body{margin:0;padding:34px 20px 80px;background:var(--bg);color:var(--ink);
     font:16.5px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.wrap{max-width:580px;margin:0 auto}
h1{font-size:22px;margin:0 0 6px}
.sub{color:var(--muted);font-size:14px;margin:0 0 28px}
.thread{border-left:2px solid var(--line);padding-left:16px}
.post{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:15px 17px 11px;margin:0 0 13px}
.text{white-space:pre-wrap;margin:0 0 10px}
img{width:100%;border-radius:10px;display:block;border:1px solid var(--line)}
.alt{color:var(--muted);font-size:13px;margin:9px 0 0;padding-left:10px;border-left:2px solid var(--line)}
.meta{color:var(--muted);font-size:12px;margin-top:9px}
"""
    out = ['<meta charset="utf-8">', f"<title>Carnegie — opening thread</title>", f"<style>{css}</style>", "<div class=wrap>",
           "<h1>Every Carnegie Library — opening thread</h1>",
           f"<p class=sub>29 August 2026. {len(POSTS)} posts, longest "
           f"{max(len(t) for t, _ in POSTS)} of 300.</p>", "<div class=thread>"]
    for i, (t, has_img) in enumerate(POSTS, 1):
        out.append("<div class=post>"
                   f"<p class=text>{html.escape(t)}</p>"
                   + (f'<img loading=lazy src="{html.escape(img)}" alt="">'
                      f'<p class=alt><b>Alt:</b> A.I.-written description: {html.escape(ALT)}</p>'
                      if has_img else "")
                   + f"<p class=meta>{i}/{len(POSTS)} · {len(t)} chars</p></div>")
    out += ["</div>", "</div>"]
    Path(__file__).resolve().parent.joinpath("data/launch_thread.html").write_text(
        "\n".join(out), encoding="utf-8")
    print("\nwrote data/launch_thread.html")
