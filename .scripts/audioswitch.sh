#!/usr/bin/env sh

if pgrep -x "mpd" > /dev/null
	then
	# Terminate already mpd instances
	killall -q mpd

	# Wait until the processes have been shut down
	while pgrep -x mpd >/dev/null; do sleep 1; done

	# Launch mopidy
	mopidy &

	echo "Mopidy launched."
	exit
fi

if pgrep -x "mopidy" > /dev/null
	then
	# Terminate already mopidy instances
        killall -q mopidy

        # Wait until the processes have been shut down
        while pgrep -x mopidy >/dev/null; do sleep 1; done

        # Launch mpd
        mpd &

        echo "mpd launched."
	exit
fi

echo "No audio players active."
exit
