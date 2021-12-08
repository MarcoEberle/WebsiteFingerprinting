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

# MODAL BOX 18 plus or accept terms | gmx.net ebay-kleinanzeigen.de  chaturbate.com livejasmin.com bongacams.com xhamster.com chip.de bild.de fandom.com n-tv.de zdf.de telekom.com
# kann keine videos abspielen ohne erweiterung | twitch.tv
# lädt nicht | zoom.us idealo.de
CLEAN_WEBSITES=(
youtube.com amazon.com ebay.com wikipedia.org web.de aparat.com facebook.com 
mail.ru ok.ru t-online.de yahoo.com netflix.com bing.com vk.com reddit.com
live.com digikala.com varzesh3.com otto.de microsoft.com yandex.ru telewebion.com
spiegel.de chip.de bild.de ebay-kleinanzeigen.de n-tv.de msn.com paypal.com rokna.net telekom.com tagesschau.de namasha.com dhl.de google.com commerzbank.de
DIRTY_WEBSITES=( pornhub.com xvideos.com bongacams.com chaturbate.com xhamster.com livejasmin.com 
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
