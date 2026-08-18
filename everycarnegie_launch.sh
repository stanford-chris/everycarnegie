#!/bin/bash
# everycarnegie_launch.sh — the one-off opening, 29 August 2026.
#
# Pins the credits note, posts the seven-post thread, then removes its own
# launchd job so it can never fire again. The daily job takes over 15 minutes
# later with the first library.
#
# ⚠️ Timing. This runs at 20:45 Asia/Seoul, which is 07:45 US Eastern and 12:45
# in Britain — the 29th in all three. The other daily slot, 09:00 Seoul, would
# have been 20:00 Eastern on the 28th, and the thread says "opened 143 years ago
# today". For an American audience, and 88% of this corpus is American, that
# would have been a day early.
#
# ⚠️ It does NOT self-remove if the thread fails. A half-posted thread has to be
# repaired by hand, and leaving the job in place is the only signal that
# something needs looking at. The poster refuses to run twice regardless.

export PATH="/Library/Frameworks/Python.framework/Versions/3.13/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
PY="/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"
HERE="$(cd "$(dirname "$0")" && pwd)"
LABEL="com.chrisstanford.everycarnegie-launch"

say() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)  $*"; }
notify() { osascript -e "display notification \"$1\" with title \"Every Carnegie Library\"" 2>/dev/null; }

say "=== opening Every Carnegie Library ==="

say "--- credits note"
"$PY" "$HERE/everycarnegie_post.py" --pin
pin_rc=$?
[ $pin_rc -ne 0 ] && say "!! the credits note failed (exit $pin_rc); continuing to the thread anyway"

say "--- opening thread"
"$PY" "$HERE/everycarnegie_post.py" --launch
launch_rc=$?

if [ $launch_rc -ne 0 ]; then
  say "!! the thread failed (exit $launch_rc). Leaving this job in place deliberately."
  notify "Launch FAILED. See ~/Library/Logs/everycarnegie-launch.log"
  exit $launch_rc
fi

say "--- removing this one-off job"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null
rm -f "$HOME/Library/LaunchAgents/$LABEL.plist"
notify "Posted. The daily job takes over at 21:00."
say "=== done. The daily job posts the first library at 21:00. ==="
