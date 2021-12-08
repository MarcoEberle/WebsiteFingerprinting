#!/bin/bash

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

create_fingerprint () {
	rm tor-browsers/tor-browser-1/Browser/TorBrowser/Data/Tor/state
	tcpdump -i lo -n -vvv -tttt port 9150 > traces/"$FILE_NAME" & tcpdumpPID=$!
	./tor-browsers/tor-browser-1/Browser/start-tor-browser "$WEBSITE" & torPID=$!
	echo "$torPID $tcpdumpPID"
}

while true
do
	TIMESTAMP=$(date +"%d.%m_%H:%M:%S.%N")
	FILE_NAME="${WEBSITE}_${TIMESTAMP}"
	echo "Website Fingerprint of $WEBSITE starts at $TIMESTAMP"
	PID="$(create_fingerprint)"
	echo "PID from call_website $PID"
	echo $$
	sleep 120
	pkill firefox --signal SIGTERM
	pkill tcpdump
	sleep 180
	#kill -TERM -- -$$
	# rm -r tor-browsers/tor-browser-1/Browser/TorBrowser/Data/Browser/Caches/*
	# cp -r tor-browsers/tor-browser-1/Browser/TorBrowser/Data/Browser/profile.default.example tor-browsers/tor-browser-1/Browser/TorBrowser/Data/Browser/Caches/profile.default
done
