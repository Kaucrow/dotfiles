#!/usr/bin/env sh

if pgrep -x "polybar" > /dev/null
	then
	
	# Terminate already running Polybar instances
	killall -q polybar 

	echo "Polybar terminated."
	exit
        
else

	# Launch Polybar 
	~/.scripts/polylaunch.sh &

	echo "Polybar launched."
	exit
fi

echo "An error has occured on Polybar switch script."
exit
