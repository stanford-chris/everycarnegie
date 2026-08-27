#!/bin/bash
# everycarnegie_launch.sh — the one-off opening, 29 August 2026.
#
# Pins the credits note, posts the two-post opening thread, then removes its own
# launchd job so it can never fire again. The daily job takes over at 23:00
# with the first library.
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
# ⚠️ THE ORDER HERE IS LOAD-BEARING, and it used to be the other way round.
#
# `launchctl bootout` terminates this job's own processes, so the script dies
# ON that line: with the bootout first, the rm, the notification and the final
# log line never ran at all. The plist survived, and because
# ~/Library/LaunchAgents is auto-loaded at login the "one-off" came back.
# StartCalendarInterval has NO year field, so `Month 8, Day 29` is every
# 29 August: this would have re-pinned the credits note and re-posted the
# opening thread on 29 August 2027.
#
# The identical bug in emoji_audit_oneoff.sh ran on 31 July 2026 and was found
# still loaded on 19 August, three weeks later, having looked perfectly
# successful the whole time. See reference_launchd_self_removing_job.
#
# So: delete the plist and say everything worth saying FIRST. The bootout goes
# last and is allowed to kill us, because by then nothing is left to do.
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
rm -f "$PLIST"
if [ -e "$PLIST" ]; then
  # Deleting the plist is the half that actually matters, so a failure here is
  # worth shouting about rather than assuming.
  say "!! $PLIST is STILL THERE. Remove it by hand or this fires again on 29 Aug 2027."
  notify "Posted, but the one-off job did not remove itself. See the log."
else
  say "    plist deleted; the job cannot reload at login"
  notify "Posted. The daily job takes over at 23:00."
fi
say "=== done. The daily job posts the first library at 23:00. ==="

# Last, deliberately: this terminates the script, so nothing may follow it.
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null
