#!/usr/bin/env python3
"""
Post one Carnegie library to Bluesky, with a freely-licensed photograph.

Reads data/carnegie_images.csv, takes the next library in a fixed shuffled
order, and posts its place, address, grant and what became of the building.

Only rows marked postable=yes are eligible. That column is yes only when the
row has an image, a resolvable photographer and a country that is not held
back: an uncredited CC BY-SA image breaches the licence, so a missing credit
blocks the post rather than degrading it.

⚠️ The post text is NOT built here. carnegie_post_preview.build() is the single
source of truth for wording, date style, the 300-character trimming order and
the credit cleanup, and this module reconstructs that exact string as a
TextBuilder so the photographer's name can carry a link. Two formatters would
drift, and the one that drifts silently is the one nobody previews.

State is data/post_state.json: posted ids plus the running order, so the
sequence survives a roster rebuild.

Requires:
    security add-generic-password -a "everycarnegie.bsky.social" \
        -s "everycarnegie-bluesky" -w

Usage:
    python3 everycarnegie_post.py             # post one
    python3 everycarnegie_post.py --dry-run   # print it, post nothing
    python3 everycarnegie_post.py --count 3
    python3 everycarnegie_post.py --pin       # post the credits and pin them
"""

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import random
import re
import subprocess
import sys
import time
from pathlib import Path

import requests
from atproto import Client, client_utils, exceptions, models

HERE = Path(__file__).resolve().parent
DATA = HERE / 'data'
MANIFEST = DATA / 'carnegie_images.csv'
ROSTER = DATA / 'carnegie_roster.csv'
STATE_FILE = DATA / 'post_state.json'
ALT_PATH = DATA / 'alt_text.json'

HANDLE = 'everycarnegie.bsky.social'
KEYCHAIN_SERVICE = 'everycarnegie-bluesky'
USER_AGENT = ('everycarnegie-bot/0.1 (https://chris-stanford.com; '
              'stanfordc+claude@mac.com)')

MAX_IMAGE_BYTES = 950_000    # under Bluesky's ~1 MB blob limit
ALT_MAX = 1900
SHUFFLE_SEED = 20260829      # the launch date, fixed so the order is reproducible

AI_PREFIX = 'A.I.-written description:'
CREDITS_HEADING = 'Sources and credits 📚'
CREDITS_PATTERN = re.compile(r'^\s*Sources and credits\b', re.I)

_spec = importlib.util.spec_from_file_location('cp', HERE / 'carnegie_post_preview.py')
cp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cp)


# --------------------------------------------------------------- credentials


def keychain_password(account, service):
    r = subprocess.run(
        ['security', 'find-generic-password', '-a', account, '-s', service, '-w'],
        capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        sys.exit(f'No Bluesky app password in the keychain for {account}.\n'
                 f'  security add-generic-password -a "{account}" '
                 f'-s "{service}" -w')
    return r.stdout.strip()


def login_client(retries=4):
    """Log in, retrying transient network failures at fire time.

    Only the login retries. A failed send_images is left to fail: a timeout
    there cannot distinguish a post that never landed from one that landed with
    the response lost, and retrying the second case double-posts.
    """
    password = keychain_password(HANDLE, KEYCHAIN_SERVICE)   # outside the loop:
    last = None                                              # missing key is not transient
    for attempt in range(retries):
        try:
            client = Client()
            client.login(HANDLE, password)
            return client
        except exceptions.NetworkError as exc:
            last = f'{type(exc).__name__}: {exc}'
            print(f'Login attempt {attempt + 1}/{retries} failed ({last})')
            if attempt + 1 < retries:
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(f'Could not log in after {retries} attempts: {last}')


# --------------------------------------------------------------------- state


def library_id(row):
    """Must match carnegie_describe.py, or every description orphans."""
    key = f"{row['name']}|{row['city']}|{row['region']}"
    return hashlib.sha1(key.encode('utf-8')).hexdigest()[:12]


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {'posted': [], 'order': []}


def save_state(state):
    tmp = STATE_FILE.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(state, indent=1))
    tmp.replace(STATE_FILE)


def load_rows():
    with MANIFEST.open() as f:
        rows = list(csv.DictReader(f))
    postable = [r for r in rows if r.get('postable') == 'yes' and r.get('photographer')]
    if not postable:
        sys.exit('No postable rows in the manifest.')
    with ROSTER.open() as f:
        notes = {(r['name'], r['city'], r['region']): r.get('notes', '')
                 for r in csv.DictReader(f)}
    return rows, postable, notes


def next_library(postable, state, skip=()):
    """Fixed shuffled order, so the feed does not march through one state at a
    time. New ids are appended rather than reshuffled, so adding libraries
    never disturbs the sequence already published."""
    by_id = {library_id(r): r for r in postable}
    order = [i for i in state.get('order', []) if i in by_id]
    known = set(order)
    fresh = sorted(i for i in by_id if i not in known)
    if fresh:
        random.Random(SHUFFLE_SEED + len(order)).shuffle(fresh)
        order += fresh
        state['order'] = order

    done = set(state.get('posted', [])) | set(skip)
    for lib_id in order:
        if lib_id not in done:
            return lib_id, by_id[lib_id]
    return None, None


# ---------------------------------------------------------------- the post


def build_post(row, note):
    """The preview's exact text, rebuilt as a TextBuilder so the photographer
    can be a link.

    CC BY-SA 4.0 s3(a)(2) allows the attribution conditions to be met "by
    providing a URI or hyperlink to a resource that includes the required
    information", and the Commons file page carries author, licence, deed link
    and source. The licence stays in plain text so the terms are still readable
    without following anything.
    """
    text = cp.build(row, note)
    tb = client_utils.TextBuilder()

    # Two links, where everylibrary deliberately carries one. There the second
    # subject would be a council's opening hours; here it is an article about
    # the building itself, and a third of these buildings are no longer
    # libraries, so the article is the only thing that can explain them. Only
    # 25% of rows have one: the link is taken from a genuine library-name
    # column, never from the city cell, whose links go to the town.
    # Link the building's own name only. cp.place() appends the region, and an
    # article about a library should not be reached by clicking "Alabama".
    place = cp.place(row)
    subject = place.split(',')[0].strip()
    article = (row.get('wikipedia_url') or '').strip()
    rest = text
    if article and text.startswith(subject):
        tb.link(subject, article)
        rest = text[len(subject):]

    who = cp.credit_name(row['photographer'])
    marker = f'📷 {who}'
    head, sep, tail = rest.partition(marker)
    if not sep or not row.get('credit_page'):
        tb.text(rest)                     # no credit page, or the name moved
        return tb
    tb.text(head + '📷 ')
    tb.link(who, row['credit_page'])
    tb.text(tail)
    return tb


_alt_cache = None


def alt_store():
    global _alt_cache
    if _alt_cache is None:
        _alt_cache = json.loads(ALT_PATH.read_text()) if ALT_PATH.exists() else {}
    return _alt_cache


def build_alt(row):
    """Describe the photograph, not the post: the place, the grant and the
    credit are all in the text immediately above it.

    Falls back to bare identification where no description has been generated.
    Worse than a description, better than nothing, and deliberately carrying no
    A.I. prefix, because nothing here was written by one.
    """
    entry = alt_store().get(library_id(row), {})
    visual = entry.get('visual')
    if visual:
        return f'{AI_PREFIX} {visual}'[:ALT_MAX]
    return f'Photograph of the Carnegie library at {cp.place(row)}.'[:ALT_MAX]


# --------------------------------------------------------------- the image


def commons_filepath_url(image_title, width):
    fname = image_title.replace('File:', '').replace(' ', '_')
    return (f'https://commons.wikimedia.org/wiki/Special:FilePath/'
            f'{requests.utils.quote(fname)}?width={width}')


def downscale(data, max_bytes=MAX_IMAGE_BYTES):
    from PIL import Image
    img = Image.open(io.BytesIO(data))
    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')
    for scale in (1.0, 0.8, 0.6, 0.45):
        buf = io.BytesIO()
        img.resize((int(img.width * scale), int(img.height * scale))).save(
            buf, format='JPEG', quality=86, optimize=True)
        if buf.tell() <= max_bytes:
            return buf.getvalue()
    return buf.getvalue()


def fetch_image(row, retries=3):
    """Every image here is on Commons, so widths are stepped down until the
    payload fits rather than pulling an original and shrinking it locally.
    Retries because these bots have died on a one-off EHOSTUNREACH at fire time.
    """
    session = requests.Session()
    session.headers.update({'User-Agent': USER_AGENT})
    last = None
    for url in (commons_filepath_url(row['image_title'], w)
                for w in (1200, 1000, 800, 640, 500)):
        for attempt in range(retries):
            try:
                r = session.get(url, timeout=45)
                if r.status_code == 200 and len(r.content) > 1000:
                    return r.content if len(r.content) <= MAX_IMAGE_BYTES \
                        else downscale(r.content)
                last = f'HTTP {r.status_code}'
            except requests.RequestException as exc:
                last = f'{type(exc).__name__}: {exc}'
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Could not fetch image for {row['name']}: {last}")


# -------------------------------------------------------------- the credits


def build_credits():
    """Attribution that will not fit in a bio, and links that a bio cannot
    carry: Bluesky bios have no link facets.

    Wikipedia's credit is a licence condition, not politeness. The "what became
    of it" line in every post is its prose, lightly trimmed, so CC BY-SA covers
    the text as well as the pictures.
    """
    with ROSTER.open() as f:
        roster = [r for r in csv.DictReader(f) if r['kind'] == 'public']
    with MANIFEST.open() as f:
        held = {r['country'] for r in csv.DictReader(f)
                if r['postable'] != 'yes' and r['image_source']}
    covered = sum(1 for r in roster if r['country'] not in {'Ireland'})

    tb = client_utils.TextBuilder()
    tb.text(CREDITS_HEADING + '\n\n')
    tb.text('Photographs: ')
    tb.link('Wikimedia Commons', 'https://commons.wikimedia.org')
    tb.text(' contributors, credited by name on every post.\n\n')
    tb.text('Libraries, grants and dates: ')
    tb.link("Wikipedia's lists of Carnegie libraries",
            'https://en.wikipedia.org/wiki/'
            'List_of_Carnegie_libraries_in_the_United_States')
    tb.text(' (CC BY-SA).\n\n')
    # Counted, not typed: a hardcoded figure goes stale the moment the roster
    # grows, and this one is a claim about completeness.
    tb.text(f'{covered:,} of the 2,509 he built; the 660 in Britain and '
            'Ireland are not yet included.')
    return tb


def pin_credits(dry_run=False):
    tb = build_credits()
    text = tb.build_text()
    print('-' * 60)
    print(text)
    print(f'[{len(text)} chars]')
    if dry_run:
        print('\nDry run: not posted, profile untouched.')
        return

    client = login_client()
    existing = client.app.bsky.actor.profile.get(client.me.did, 'self')
    old = existing.value.pinned_post
    if old:
        try:
            rec = client.get_post(old.uri.rsplit('/', 1)[-1],
                                  profile_identify=client.me.did)
            if CREDITS_PATTERN.match(rec.value.text):
                client.delete_post(old.uri)
                print('Replaced the previous credits post.')
            else:
                print('Pinned post is not the credits note; leaving it alone.')
        except Exception as exc:
            print(f'Could not inspect the pinned post ({exc}); leaving it alone.')

    posted = client.send_post(text=tb, langs=['en'])
    existing = client.app.bsky.actor.profile.get(client.me.did, 'self')
    profile = existing.value
    profile.pinned_post = models.ComAtprotoRepoStrongRef.Main(
        uri=posted.uri, cid=posted.cid)
    client.com.atproto.repo.put_record(models.ComAtprotoRepoPutRecord.Data(
        repo=client.me.did, collection='app.bsky.actor.profile', rkey='self',
        record=profile, swap_record=existing.cid))
    print('Posted and pinned.')


# ---------------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dry-run', action='store_true', help='print the post without posting')
    ap.add_argument('--count', type=int, default=1, help='how many to post (default 1)')
    ap.add_argument('--pin', action='store_true', help='post the credits note and pin it')
    args = ap.parse_args()

    if args.pin:
        pin_credits(dry_run=args.dry_run)
        return

    rows, postable, notes = load_rows()
    state = load_state()
    print(f'{len(postable)} postable of {len(rows)} libraries; '
          f'{len(state.get("posted", []))} already posted')

    client = None
    previewed = []            # dry runs write no state, so advance locally
    for n in range(args.count):
        lib_id, row = next_library(postable, state, skip=previewed)
        if not row:
            print('Nothing left to post: the whole corpus has been through.')
            break

        note = cp.clean_note(notes.get((row['name'], row['city'], row['region']), ''))
        tb = build_post(row, note)
        alt = build_alt(row)

        print('-' * 60)
        print(tb.build_text())
        print(f'[alt] {alt}')
        print(f'[src] {row["image_source"]} · {row["credit_page"]}')

        if args.dry_run:
            previewed.append(lib_id)
            continue

        image = fetch_image(row)
        if client is None:
            client = login_client()

        # Without an aspect ratio Bluesky guesses, then reflows or crops once
        # the image loads.
        from PIL import Image
        with Image.open(io.BytesIO(image)) as im:
            ratio = models.AppBskyEmbedDefs.AspectRatio(width=im.width, height=im.height)

        client.send_images(text=tb, images=[image], image_alts=[alt],
                           image_aspect_ratios=[ratio], langs=['en'])
        state.setdefault('posted', []).append(lib_id)
        save_state(state)
        print(f'Posted ({len(state["posted"])}/{len(postable)}).')

        if n + 1 < args.count:
            time.sleep(2)

    if args.dry_run:
        print('\nDry run: nothing posted, no state written.')


if __name__ == '__main__':
    main()
