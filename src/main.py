import datetime
import shutil
import subprocess
from multiprocessing import Process
from time import sleep
import time
import stem.process
from requests import RequestException
from stem import Signal
from stem.control import Controller
import requests
import os
import logging
from fake_headers import Headers


# TODO: add https://askubuntu.com/questions/530920/tcpdump-permissions-problem
# sudo chgrp <user_running_this_code> /usr/sbin/tcpdump
# sudo chmod 750 /usr/sbin/tcpdump
def create_fingerprint(url, port, proxy, time_to_launch_tor):
    print("Creating Fingerprint of:", url, port)
    full_url = "https://www." + url + "/"
    timestamp = datetime.datetime.now().strftime("%d.%m_%H:%M:%S.%f")
    print(timestamp)
    file = open("traces/" + timestamp + "_" + url + ".txt", "w")
    tcpdump = subprocess.Popen(['tcpdump', '-i', 'lo', '-n', '-vv', '-tttt', '-l', 'port', port], stdout=file)
    sleep(5)
    header = get_header()
    status_code = 0
    try:
        start_trace_time = time.time()
        response = requests.get(full_url, proxies=proxy, headers=header, timeout=240)
        end_trace_time = time.time()
        time_to_trace = end_trace_time - start_trace_time
        status_code = response.status_code
        status_logger.info(url + " : " + str(status_code))
        print(response.status_code, url)
        # print(requests.get("http://httpbin.org/ip", proxies=proxy, headers=header).text)
    except RequestException as req_ex:
        print(url + " : ", str(req_ex))
        error_logger.info(timestamp + " : " + url + " : " + str(req_ex))
        pass
    finally:
        tcpdump.kill()
        tcpdump.wait()
        file.write(str(status_code) + ", " + str(time_to_launch_tor) + ", " + str(time_to_trace))
        file.close()

    # change_exit_node(port)


def start_tor_process(torrc, url, port, proxy):
    print("Launching: " + torrc)
    try:
        start_tor_time = time.time()
        stem.process.launch_tor(torrc_path=torrc, take_ownership=True, completion_percent=100, timeout=300)
        end_tor_time = time.time()
        print(end_tor_time - start_tor_time)
        time_to_launch_tor = end_tor_time - start_tor_time
        # run trace the traces here
        create_fingerprint(url, port, proxy, time_to_launch_tor)
        print("done", torrc)
    except OSError as start_error:
        print(start_error)
        error_logger.info(torrc + " : " + str(start_error))


# Open a new circuit and get a new exit node, e.g. new IP address.
def change_exit_node(port):
    control_port = int(port) + 1
    try:
        with Controller.from_port(port=control_port) as controller:
            controller.authenticate()
            if controller.is_newnym_available():
                controller.signal(Signal.NEWNYM)
                sleep(5)
    except stem.SocketError as stem_error:
        print(stem_error)
        error_logger.info(port + " : " + str(stem_error))


# Remove data directory to force tor to create new circuit
def change_tor_circuit():
    for files in os.listdir(path_to_data_directory):
        path = os.path.join(path_to_data_directory, files)
        try:
            shutil.rmtree(path, ignore_errors=True)
        except OSError:
            os.remove(path)


# TODO: Change at home to all_websites and on HM to clean_websites
def get_new_url():
    return unmonitored_websites[current_url_index % len(unmonitored_websites)]


def get_new_port():
    return ports[current_port_index % max_tors]


def get_header():
    header = Headers(
        browser="firefox",
        os="random",
        headers=True  # generate misc headers
    )
    return header.generate()

# TODO: Dauer wie lange der Verbindungsaufbau gebraucht hat und wie lange der Download dauerte
if __name__ == '__main__':
    status_logger = logging.getLogger("status")
    error_logger = logging.getLogger("error")
    status_logger.setLevel(logging.INFO)
    error_logger.setLevel(logging.INFO)
    fh_status = logging.FileHandler("status.log", "a")
    status_logger.addHandler(fh_status)
    fh_error = logging.FileHandler("error.log", "a")
    error_logger.addHandler(fh_error)
    
    unmonitored_websites = ["telegram.org", "python.org", "raspberrypi.org", "microsoft.org", "telegram.org",
                            "dictionary.com", "torproject.org", "yelp.com", "indeed.com", "target.com",
                            "nytimes.com", "mayoclinic.org", "espn.com", "timeweb.ru", "mit.edu",
                            "linktr.ee", "hm.com", "irs.gov", "nih.gov", "steampowered.com",
                            "foxnews.com", "quora.com", "bestbuy.com", "ca.gov", "play.google.com",
                            "cnet.com", "usnews.com", "zillow.com", "businessinsider.com", "bulbagarden.net",
                            "genuis.com", "realtor.com", "fedex.com", "bankofamerica.com", "washingtonpost.com",
                            "investopedia.com", "speedtest.net", "spotify.com", "dcd.gov", "chase.com",
                            "hulu.com", "xfinity.com", "forbes.com", "wowhead.com", "expedia.com",
                            "urbandictionary.com", "foodnetwork.com", "nbcnews.com", "macys.com", "ign.com",
                            "capitalone.com", "costco.com", "theguardian.com", "apartments.com", "cnbc.com",
                            "glassdoor.com", "yellowpages.com", "att.com", "variety.com", "bbc.com",
                            "khanacademy.org", "adobe.com", "cbssports.com", "verizon.com", "dictionary.com",
                            "ria.ru", "ftc.gov", "pinterest.fr", "bloglovin.com", "vice.com",
                            "orange.fr", "cnil.fr", "discord.com", "naver.com", "sputniknews.com",
                            "rt.com", "sciencedaily.com", "ted.com", "outlook.com", "newsweek.com",
                            "sapo.pt", "secureserver.net", "hp.com", "playstation.com", "pexels.com",
                            "ea.com", "cambridge.org", "apache.org", "ohv.com", "wiley.com",
                            "offset.com", "ziddu.com", "ibm.com", "cbc.ca", "deezer.com",
                            "mega.nz", "metro.co.uk", "ox.ac.uk", "pixabay.com", "canva.com",
                            "dreniq.com", "gfycat.com", "slashdot.org", "depositfiles.com", "cornell.edu",
                            "addthis.com", "e-monsite.com", "netlify.app", "cornell.edu", "addthis.com",
                            "stackoverflow.com", "elmundo.es", "addtoany.com", "smh.com.au", "ietf.org",
                            "pbs.org", "tripadivsor.com", "nginx.org", "biglobe.ne.jp", "themeforest.net",
                            "rtve.es", "rambler.ru", "sfgate.com", "imageshack.com", "zoom.us",
                            "gnu.org", "techcrunch.com", "clarin.com", "ca.gov", "rakuten.co.jp",
                            "buzzfeed.com", "netflix.com", "mashable.com", "aljazeera.com", "plos.org",
                            "lexpress.fr", "thenai.org", "detik.com", "gizmodo.com", "as.com",
                            "wikihow.com", "trello.com", "weibo.com", "latimes.com", "doi.org",
                            "kickstarter.com", "eventbrite.com", "tes.com", "mozilla.com", "alicdn.com",
                            "php.net", "nationalgeographic.com", "theatlantic.com", "samsung.com", "lemonde.fr",
                            "disney.com", "whitehouse.gov", "yandex.ru", "reuters.com", "hatena.ne.jp",
                            ]
    clean_websites = ["kaufland.de", "ninisite.com", "delgarm.com", "pinterest.de", "linkedin.com", "gls-pakete.de",
                      "instagram.com", "welt.de", "amazon.com", "varzesh3.com", "wetter.com", "chefkoch.de",
                      "youtube.com", "ebay.de", "wikipedia.org", "web.de", "aparat.com", "facebook.com", "filmix.ac",
                      "tiktok.com", "twitter.com", "netflix.com", "dhl.de", "mail.ru", "ok.ru", "t-online.de",
                      "yahoo.com", "bing.com", "vk.com", "whatsapp.com", "reddit.com", "live.com", "digikala.com",
                      "microsoft.com", "yandex.ru", "focus.de", "telewebion.com", "fandom.com", "spiegel.de", "chip.de",
                      "bild.de", "zalando.de", "n-tv.de", "msn.com", "paypal.com", "rokna.net", "telekom.com",
                      "tagesschau.de", "namasha.com", "google.com", "commerzbank.de", "zdf.de", "twitch.tv",
                      "arbeitsagentur.de", "booking.com"]  # 54

    dirty_websites = ["xvideos.com", "xnxx.com", "livejasmin.com"]  # 3

    all_websites = clean_websites + dirty_websites + dirty_websites

    ports = [
        "9150", "9250", "9350", "9450",
        "9550", "9650", "9750", "9850",
        "9950", "10050", "10150", "10250",
        "10350", "10450", "10550", "10650",
        "10750", "10850", "10950", "11050",
        "11150", "11250", "11350", "11450",
        "11550", "11650", "11750", "11850",
        "11950", "12050", "12150", "12250",
    ]

    torrc_path = "/etc/tor/torrc."
    path_to_data_directory = "/home/user/Desktop/TorDataDirectory/"
    # Create TorDataDirectory to save Tor Data e.g. Entry Guards
    if not os.path.exists(path_to_data_directory):
        os.makedirs(path_to_data_directory)
    # Create traces folder
    if not os.path.exists('traces'):
        os.makedirs('traces')
    current_url_index = 0
    current_port_index = 0
    change_tor_circuit()

    max_tors = 32

    while True:
        tor_processes = []

        for torrc_index in range(1, max_tors + 1):
            current_url = get_new_url()
            current_port = get_new_port()
            proxies = {
                'http': 'socks5://localhost:' + current_port,
                'https': 'socks5://localhost:' + current_port
            }
            path = torrc_path + str(torrc_index)
            tor_processes.append(Process(target=start_tor_process, args=(path, current_url, current_port, proxies)))
            current_url_index += 1
            current_port_index += 1

        for tor in tor_processes:
            tor.start()

        for tor in tor_processes:
            tor.join()

        sleep(1)
        change_tor_circuit()
        sleep(10)
