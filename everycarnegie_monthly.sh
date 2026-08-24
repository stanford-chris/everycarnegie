#!/bin/bash
# everycarnegie_monthly.sh — the monthly photograph re-sweep.
#
# Two steps:
#
#   1. carnegie_images.py            Forgets the "nothing found" memos and looks
#      --recheck-misses              again for photographs, then rebuilds the
#                                    manifest.
#   2. carnegie_describe.py          Alt text for whatever step 1 found. A new
#                                    photograph with no description is not
#                                    postable, so this is not optional.
#
# ⚠️ This exists because nothing here ever looked twice. Every stage memoises
# its misses permanently, so re-running carnegie_images.py found nothing however
# often it ran: --recheck-misses is what expires those memos. Ported from
# everylibrary_monthly.sh step 4 on 24 August 2026, along with the correctness
# rule that makes it safe — a library that already HAS a photograph is left
# alone, because the sources are ranked and alt_text.json is keyed by library
# rather than by image, so a newly found higher-ranked file would keep the
# description written for the one it displaced.
#
# ⚠️ Ireland is the sharpest case this is aimed at: 56 libraries in the roster
# and, as of 24 August 2026, not one with a usable free photograph. Britain has
# 245 rows and 145 postable. Neither gap closes on its own.
#
# ⚠️ Britain's LARGER gap is the roster, not photographs, and this pass cannot
# touch it: the manifest holds 301 British and Irish rows against roughly 660
# built. The better source, Cardiff's AHRC "Shelf Life" gazetteer, is
# CC BY-NC-SA and incompatible with the roster's CC BY-SA in both directions.
# See britain_options.py. Do not read a quiet month here as "Britain is done".
#
# ⚠️ Both steps run regardless of what the previous returned, and `set -e` is
# deliberately NOT in force around them: a failed sweep is no reason to skip
# describing photographs an earlier sweep already found. The exit code is the
# worst of the two, so launchd still records a failure.

export PATH="/Library/Frameworks/Python.framework/Versions/3.13/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
PY="/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"
HERE="$(cd "$(dirname "$0")" && pwd)"
MANIFEST="$HERE/data/carnegie_images.csv"

worst=0
step() {
    local label="$1"; shift
    echo "== $label"
    "$@"
    local rc=$?
    if [ "$rc" -ne 0 ]; then
        echo "!! $label FAILED (exit $rc)"
        [ "$rc" -gt "$worst" ] && worst=$rc
    fi
    return 0
}

echo "everycarnegie monthly pass, $(date '+%Y-%m-%d %H:%M %Z')"

# Counted before and after, so the log says what the sweep actually bought
# rather than only that it ran.
before=$("$PY" - "$MANIFEST" <<'PYEOF'
import csv, sys
try:
    with open(sys.argv[1]) as f:
        print(sum(1 for r in csv.DictReader(f)
                  if r['postable'] == 'yes' and r['photographer']))
except OSError:
    print(-1)
PYEOF
)

step "images --recheck-misses" "$PY" "$HERE/carnegie_images.py" --recheck-misses
step "describe"               "$PY" "$HERE/carnegie_describe.py"

after=$("$PY" - "$MANIFEST" <<'PYEOF'
import csv, sys
try:
    with open(sys.argv[1]) as f:
        print(sum(1 for r in csv.DictReader(f)
                  if r['postable'] == 'yes' and r['photographer']))
except OSError:
    print(-1)
PYEOF
)

# ⚠️ A FALL is reported, never silently accepted. It should not happen: this
# pass only ever expires memos for libraries that have nothing, so the postable
# count can rise or hold. A drop means something else changed underneath.
if [ "$before" -ge 0 ] && [ "$after" -ge 0 ]; then
    echo "postable: $before -> $after"
    if [ "$after" -lt "$before" ]; then
        echo "!! postable count FELL by $((before - after)); nothing here should reduce it"
        [ "$worst" -eq 0 ] && worst=1
    fi
else
    echo "!! could not read the manifest to compare postable counts"
    [ "$worst" -eq 0 ] && worst=1
fi

echo "done (exit $worst)"
exit "$worst"
