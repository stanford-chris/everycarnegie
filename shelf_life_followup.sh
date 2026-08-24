#!/bin/bash
# shelf_life_followup.sh — a one-off reminder, 15 September 2026.
#
# Emails a prompt to follow up with Professor Oriel Prizeman at Cardiff about
# the Carnegie Libraries of Britain gazetteer, then deletes itself.
#
# ⚠️ Belt to a Reminders braces. The reminder set on 24 August 2026 lives in a
# list holding 2,056 items, where a single entry three weeks out is easy to
# lose. This puts it in the inbox instead, under the [claude] prefix the
# `Claude Tasks` mail rule already files.
#
# ⚠️ StartCalendarInterval HAS NO YEAR FIELD. "Month 9, Day 15" is EVERY
# 15 September, so without the teardown below this nags annually for ever. That
# exact bug ran in emoji_audit_oneoff.sh on 31 July 2026 and was still loaded
# three weeks later, looking successful the whole time.
#
# ⚠️ Ordering is load-bearing, and it is the one thing to get right here: the
# `rm` comes FIRST and is CHECKED, and the `bootout` comes LAST because it
# terminates this script. A job cannot bootout and then tidy up after itself:
# it dies mid-line and the plist reloads at login. See
# reference_launchd_self_removing_job.

export PATH="/Library/Frameworks/Python.framework/Versions/3.13/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
PY="/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"
LABEL="com.chrisstanford.shelflifefollowup"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

say() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*"; }

say "=== shelf life follow-up reminder ==="

"$PY" /Users/christopherstanford/Scripts/estate_mail.py \
  "[claude] Cardiff Shelf Life: follow up due" <<'BODY'
The licensing letter to Professor Oriel Prizeman went on 24 August 2026, to
Shelf-lifeproject@cardiff.ac.uk, cc prizemano@cardiff.ac.uk. Her auto-reply said
she was on annual leave until 1 September, so silence before then meant nothing.
It has been about a fortnight since she was back.

The ask: would they release the Carnegie Libraries of Britain gazetteer data
alone, not the photographs, under CC BY-SA 4.0 or CC BY 4.0, so it can share a
file with the Wikipedia-derived roster.

This is not urgent and it is not a blocker. The two-file fallback needs nobody's
permission, and the bot has been posting British libraries from Wikipedia's rows
since early September. One short follow-up is reasonable; a second would not be.

The letter, and everything decided about it, is in the docstring of
~/Scripts/everycarnegie/shelf_life_email.py. If they say yes, the Cardiff credit
must go into build_credits() before any British library posts from their records
— everycarnegie_post.py refuses to build the credits note once
data/clb_gazetteer.csv exists and the note does not name them.

This job has now deleted itself and will not write again.
BODY
rc=$?
[ "$rc" -ne 0 ] && say "!! estate_mail.py FAILED (exit $rc); the reminder did not send"

# Delete the plist FIRST and check it, because this is the half that stops the
# annual repeat. Shout if it failed: a silent survivor is the whole bug.
rm -f "$PLIST"
if [ -e "$PLIST" ]; then
    say "!! $PLIST is STILL THERE. Remove it by hand or this fires again on 15 Sep 2027."
    osascript -e 'display notification "One-off follow-up job did not remove itself." with title "Shelf Life reminder"' 2>/dev/null
else
    say "    plist deleted; the job cannot reload at login"
fi
say "=== done ==="

# Last, deliberately: this terminates the script, so nothing may follow it.
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null
