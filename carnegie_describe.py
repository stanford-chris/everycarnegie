#!/usr/bin/env python3
"""
carnegie_describe.py — alt text for the Carnegie photographs.

This deliberately does not reimplement the description logic. everylibrary's
describer already carries guards that were each added after a specific failure
reached a real post, and rewriting them here would mean rediscovering the same
faults on a new corpus. It imports that module and reuses:

  not_a_description  Filters the two ways the model returns prose that is not a
                     description: refusals, and commentary correcting the brief.
                     One such reply would have published a local file path.
  describe()         Two independent reads of every image, kept only if they
                     agree on storey count and indoor/outdoor. A fluent,
                     confident, entirely invented description is otherwise
                     indistinguishable from a real one.

⚠️ TMP_DIR is overridden, and that is load-bearing. `claude -p` reads the image
through Claude Code's Read tool, which refuses any path outside its working
directory. Left pointing at everylibrary/data/_tmp, every call from this
directory would fail — and fail politely, with exit code 0 and a sentence about
not having a tool available, which is exactly the shape of a string that could
be stored as a description by mistake.

Output is data/alt_text.json, keyed by the same id the poster will use, so it
survives a roster rebuild. Resumable: interrupt it freely.

Usage:
    python3 carnegie_describe.py                 # everything outstanding
    python3 carnegie_describe.py --limit 10      # a sample, to check quality
    python3 carnegie_describe.py --workers 6
"""

import argparse
import csv
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
# everylibrary has not moved out of ~/Scripts, so this is an absolute
# reference rather than a HERE.parent sibling lookup: everycarnegie's own
# move to ~/Projects on 30 August 2026 broke the old sibling-relative form,
# since ~/Projects/everylibrary does not exist.
sys.path.insert(0, str(Path.home() / "Scripts" / "everylibrary"))
import everylibrary_describe as ed          # noqa: E402
import carnegie_post_preview as cp         # noqa: E402  (typographic)

ed.TMP_DIR = DATA / "_tmp"                  # see the warning above
ed.TMP_DIR.mkdir(parents=True, exist_ok=True)
# Since 11 September 2026 every `claude -p` call the describer makes runs
# `--restricted --tools Read` with its cwd set to a directory holding the one
# image (everylibrary_describe.CONFINED and _staged). This file makes no call
# of its own, so there is nothing to add here: the confinement arrives with the
# import, and so does independence from the launch directory. Before that date
# the describer inherited the caller's cwd and named the image by absolute
# path, and everycarnegie_monthly.sh runs this script without a cd, so where
# the model could read from depended on whoever started the run.

IMAGES = DATA / "carnegie_images.csv"
ALT_PATH = DATA / "alt_text.json"

_lock = threading.Lock()

# everylibrary_describe.py's describe() defaults to "a UK public library" /
# British English, which is right for everylibrary (100% UK) and wrong for
# this roster: 79% American, 13% UK/Ireland (measured 3 September 2026,
# data/carnegie_roster.csv). Before this, every Carnegie photo — American,
# Canadian, Trinidadian, whatever — was told to write British English, and
# 152 of 1,399 stored descriptions already showed it (colour, centre, ...).
# So spelling is chosen per row's own country, matching describe()'s two
# override kwargs; everything else (unset here) still takes its default.
UK_COUNTRIES = {"United Kingdom", "Ireland"}


def spelling_for(row):
    """(subject, spelling) for describe(), from the row's own country."""
    if row.get("country") in UK_COUNTRIES:
        return "a UK or Irish Carnegie library building", "British"
    return "a Carnegie library building", "American"


library_id = cp.library_id          # canonical definition in carnegie_post_preview.py


def load_alt():
    if ALT_PATH.exists():
        return json.loads(ALT_PATH.read_text())
    return {}


def save_alt(alt):
    tmp = ALT_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(alt, indent=1, sort_keys=True, ensure_ascii=False))
    tmp.replace(ALT_PATH)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="describe at most N (0 = all)")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()

    with IMAGES.open() as f:
        rows = [r for r in csv.DictReader(f) if r["postable"] == "yes"]
    alt = load_alt()
    todo = [r for r in rows if library_id(r) not in alt]
    if args.limit:
        todo = todo[:args.limit]

    print(f"{len(rows)} postable, {len(alt)} already described, {len(todo)} to do "
          f"({args.workers} at a time)", flush=True)
    if not todo:
        return

    env = ed.claude_env()
    session = requests.Session()
    session.headers.update({"User-Agent": ed.USER_AGENT if hasattr(ed, "USER_AGENT")
                            else "everycarnegie-bot/0.1 (https://chris-stanford.com)"})
    done = [0]
    ok = [0]
    started = time.time()

    def work(row):
        subject, spelling = spelling_for(row)
        text = ed.describe(row, session, env, subject=subject, spelling=spelling)
        with _lock:
            done[0] += 1
            if text:
                # Curled on the way in, so the store matches house style at
                # rest; the poster curls again on the way out, which is a
                # no-op on text that is already curly.
                alt[library_id(row)] = {"visual": cp.typographic(text)}
                ok[0] += 1
            if done[0] % 25 == 0 or done[0] == len(todo):
                save_alt(alt)
                rate = done[0] / max(time.time() - started, 1)
                left = (len(todo) - done[0]) / rate / 60 if rate else 0
                print(f"  {done[0]:>5}/{len(todo)}  described {ok[0]}  "
                      f"~{left:.0f} min left", flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(work, todo))

    save_alt(alt)
    print(f"\nwritten to {ALT_PATH}")
    print(f"  described {ok[0]}, failed or dropped {len(todo) - ok[0]}")


if __name__ == "__main__":
    main()
