#!/bin/bash

ctrl_c () {
	pkill firefox --signal SIGTERM
	echo "tortracer stopped fingerprinting"
	exit 0
}

trap ctrl_c INT

echo "  _                _                                "
sleep 0.1
echo " | |              | |                               "
sleep 0.1
echo " | |_  ___   _ __ | |_  _ __  __ _   ___  ___  _ __ "
sleep 0.1
echo " | __|/ _ \ | '__|| __|| '__|/ _' | / __|/ _ \| '__|"
sleep 0.1
echo " | |_| (_) || |   | |_ | |  | (_| || (__|  __/| |   "
sleep 0.1
echo "  \__|\___/ |_|    \__||_|   \__,_| \___|\___||_|   "
sleep 0.1
echo "                                                    "

echo "What website do you want to fingerprint?"
read -r WEBSITE
if [ -z "$WEBSITE" ]
then
	echo "Please enter a correct URL like 'google.com'"
	exit 1
else
	echo "Fingerprinting $WEBSITE"
fi

echo "How many Browser you want to fingerprint parallel? Choose between 1 and 16. Care for your RAM!"
read -r BROWSERS
if [ "$BROWSERS" -gt 16 ]
then
	echo "Too many Browsers chosen. Max is 16."
	exit 1
else
	echo "Browsers chosen: $BROWSERS"
fi

create_fingerprint () {
	rm tor-browsers/tor-browser-"$1"/Browser/TorBrowser/Data/Tor/state
	local SOCKSPORT=$((9150+$1))
	tcpdump -i lo -n -vvv -tttt port $SOCKSPORT > traces/"$FILE_NAME" &
	./tor-browsers/tor-browser-"$1"/Browser/start-tor-browser "$WEBSITE" &
	local PID=$! 
	echo "$PID"
}

while true;
do
	for ((i=1;i<=BROWSERS;i++));
	do
		TIMESTAMP=$(date +"%d.%m_%H:%M:%S.%N")
		FILE_NAME="${WEBSITE}_${TIMESTAMP}"
		PID="$(create_fingerprint "$i")"
		echo "PID from call_website $PID"
		sleep 1
	done
	sleep 180
	pkill firefox --signal SIGTERM
done
