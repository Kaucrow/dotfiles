#!/usr/bin/env sh

if pgrep -x "nm-applet" > /dev/null
	then
	
	# Terminate already running nm-applet instances
	killall -q nm-applet

	echo "nm-applet terminated."
	exit
        
        else

	# Launch nm-applet
	nm-applet &

	echo "nm-applet launched."
	exit
fi

echo "An error has occured on nm-applet launch script."
exit
