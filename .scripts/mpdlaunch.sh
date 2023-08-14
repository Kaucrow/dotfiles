#!/usr/bin/env sh

# Launch MPD
mpd

# Wait until MPD starts
while pgrep -x mpd <=/dev/null; do sleep 1; done

# Update the MPD database
mpc update &

echo "MPD started."
exit
