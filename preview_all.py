#!/usr/bin/env python3
"""
preview_all.py — everything the account will publish, on one page.

Built from the live code, not from copies: the pinned note comes from
build_credits(), the thread from launch_thread.POSTS, and the daily example
from build_post() on a real row. What you read here is what would go out.
"""
import html, importlib.util, json, hashlib, csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('ep', HERE / 'everycarnegie_post.py')
ep = importlib.util.module_from_spec(spec); spec.loader.exec_module(ep)

def linkify(tb):
    """Render a TextBuilder as HTML with its facets as real anchors."""
    text = tb.build_text(); raw = text.encode()
    spans = sorted(((f.index.byte_start, f.index.byte_end, f.features[0].uri)
                    for f in tb.build_facets() if hasattr(f.features[0], 'uri')))
    out, cur = [], 0
    for a, b, uri in spans:
        out.append(html.escape(raw[cur:a].decode()))
        out.append(f'<a href="{html.escape(uri)}">{html.escape(raw[a:b].decode())}</a>')
        cur = b
    out.append(html.escape(raw[cur:].decode()))
    return "".join(out), len(text)

def commons_img(title):
    import urllib.parse
    return ("https://commons.wikimedia.org/wiki/Special:FilePath/"
            + urllib.parse.quote(title.replace('File:', '').replace(' ', '_')) + "?width=1000")

rows, postable, notes = ep.load_rows()
alt = json.loads((HERE/'data/alt_text.json').read_text())
example = next(r for r in postable
               if ep.library_id(r) in alt and r['wikipedia_url'].strip() and r['grant'].strip())
note = ep.cp.clean_note(notes.get((example['name'], example['city'], example['region']), ''))

CSS = """
:root{color-scheme:light dark;--bg:#faf9f7;--card:#fff;--ink:#1a262b;--muted:#5d6b70;--line:#e3e0da;--link:#1177cc}
@media (prefers-color-scheme:dark){:root{--bg:#14191c;--card:#1c2429;--ink:#e8ddc8;--muted:#9aa8ad;--line:#2b353a;--link:#6cb6ff}}
*{box-sizing:border-box}
body{margin:0;padding:34px 20px 90px;background:var(--bg);color:var(--ink);
     font:16.5px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.wrap{max-width:580px;margin:0 auto}
h1{font-size:22px;margin:0 0 6px}
.sub{color:var(--muted);font-size:14px;margin:0 0 6px}
h2{font-size:17px;margin:44px 0 4px;padding-top:24px;border-top:1px solid var(--line)}
.why{color:var(--muted);font-size:14px;margin:0 0 16px}
.thread{border-left:2px solid var(--line);padding-left:16px}
.post{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:15px 17px 11px;margin:0 0 13px}
.text{white-space:pre-wrap;margin:0 0 10px}
a{color:var(--link)}
img{width:100%;border-radius:10px;display:block;border:1px solid var(--line)}
.alt{color:var(--muted);font-size:13px;margin:9px 0 0;padding-left:10px;border-left:2px solid var(--line)}
.meta{color:var(--muted);font-size:12px;margin-top:9px}
"""
out = ["<title>Every Carnegie Library — everything it will post</title>",
       f"<style>{CSS}</style>", "<div class=wrap>",
       "<h1>Every Carnegie Library</h1>",
       "<p class=sub>Rendered from the live code. Links are real; character counts are exact.</p>"]

# 1. pinned
body, n = linkify(ep.build_credits())
out += ["<h2>1 · The pinned post</h2>",
        "<p class=why>Posted and pinned by the one-off job at 20:45 Seoul on 29 August.</p>",
        f"<div class=post><p class=text>{body}</p><p class=meta>pinned · {n} of 300</p></div>"]

# 2. the thread
out += ["<h2>2 · The opening thread</h2>",
        "<p class=why>Seven posts, immediately after the pinned note.</p>", "<div class=thread>"]
for i, (text, has_img) in enumerate(ep.launch_thread.POSTS, 1):
    body, n = linkify(ep.build_thread_post(text))
    img = (f'<img loading=lazy src="{commons_img(ep.launch_thread.IMAGE_TITLE)}" alt="">'
           f'<p class=alt><b>Alt:</b> {html.escape(ep.AI_PREFIX + " " + ep.LAUNCH_IMAGE["alt"])}</p>'
           if has_img else "")
    out.append(f"<div class=post><p class=text>{body}</p>{img}"
               f"<p class=meta>{i}/{len(ep.launch_thread.POSTS)} · {n} of 300</p></div>")
out.append("</div>")

# 3. a daily post
body, n = linkify(ep.build_post(example, note))
out += ["<h2>3 · A regular daily post</h2>",
        "<p class=why>One of 1,223, twice a day from 21:00 Seoul on the 29th.</p>",
        f"<div class=post><p class=text>{body}</p>"
        f'<img loading=lazy src="{html.escape(example["image_url"])}" alt="">'
        f'<p class=alt><b>Alt:</b> {html.escape(ep.build_alt(example))}</p>'
        f"<p class=meta>{n} of 300 · {html.escape(example['licence'])}</p></div>", "</div>"]

(HERE/'data/preview_all.html').write_text("\n".join(out), encoding='utf-8')
print(f"pinned {len(ep.build_credits().build_text())} · thread {len(ep.launch_thread.POSTS)} posts · "
      f"daily example: {example['name']}, {example['region']}")
