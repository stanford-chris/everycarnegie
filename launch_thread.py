#!/usr/bin/env python3
"""
launch_thread.py — the opening thread for 29 August, and a page to read it on.

Six posts, one idea each: who Carnegie was, what happened in Dunfermline, what
the deal actually was, how many were built, who was shut out, and what became of
them. The last post carries the sources, so the thread can serve as the pinned
note.

⚠️ Post 1 has no "Dunfermline, Fife 📚" header, and that is arithmetic rather
than taste. Naming the town in the prose and again in a header runs the post to
315 characters. The 📚 place-header format therefore begins with the daily
posts, and the opening reads as an introduction instead of a catalogue entry.

⚠️ Post 5 is not optional. A bot posting a thousand handsome civic buildings
owes its readers the fact that in the segregated South the terms were different.

Every claim is from the Andrew Carnegie and Carnegie library articles on
Wikipedia, checked 18 August 2026: 2,509 buildings 1883–1929; the ten percent
annual commitment from public funds; about 90% of the fortune given away;
Savannah 1914; 911 of 1,681 US buildings still libraries in 1992.

Usage:
    python3 launch_thread.py          # print the thread, render the page
    open data/launch_thread.html
"""

CREDIT = "\n\n📷 Stephencdickson · CC BY-SA 3.0"

# (text, carries_the_photograph)
POSTS = [
 ("""Dunfermline, Scotland 📚

Andrew Carnegie was born here in 1835. He later became the richest man in the world, and gave away about 90% of his wealth.

Between 1883 and 1929 he paid for 2,509 public libraries. This was the first, opened 143 years ago today.""" + CREDIT, True),

 ("""His mother laid its foundation stone. He had left Scotland 35 years earlier, at 12, when his father's weaving business failed and the family sailed for Pennsylvania. In Pittsburgh, he borrowed books from a man who opened his library to working boys on Saturdays.""", False),

 ("""Carnegie credited that library with his start, and when the steel money came he spent it building more of them.""", False),

 ("""They were not gifts, though.

To get one, a town had to provide the land, pay the staff, keep it free to everyone and commit 10% of the building's cost every year, out of public taxes, to run it.""", False),

 ("""In the segregated South, Carnegie funded separate libraries for Black residents rather than requiring the existing ones to admit them. The one in Savannah, Ga., opened in 1914, for those whom the library had turned away.""", False),

 ("""Most of the libraries (nearly 1,700) were in the U.S., with 660 in Britain and Ireland and 125 in Canada.

By 1992, 911 of the buildings in the U.S. were still libraries. The others had been converted to museums, town halls, offices, houses; some were gone.""", False),

 ("""This account posts them one at a time: the building, the grant, what that money is worth now and what became of it.

1,850 of them. Britain and Ireland's 660 are not included yet.

Photos: Wikimedia Commons contributors, credited on every post.""", False),
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
    out = [f"<title>Carnegie — opening thread</title>", f"<style>{css}</style>", "<div class=wrap>",
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
