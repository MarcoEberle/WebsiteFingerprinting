import datetime
import shutil
import subprocess
from multiprocessing import Process
from time import sleep
import stem.process
from requests import RequestException
from stem import Signal
from stem.control import Controller
import requests
import os
import logging
from fake_headers import Headers


def create_fingerprint(url, port, proxy, time):
    print("Creating Fingerprint of:", url, port)
    full_url = "https://www." + url + "/"
    timestamp = datetime.datetime.now().strftime("%d.%m_%H:%M:%S.%f")
    file = open("traces/" + timestamp + "_" + url + ".txt", "w")
    tcpdump = subprocess.Popen(['tcpdump', '-i', 'lo', '-n', '-vv', '-tttt', '-l', 'port', port], stdout=file)
    sleep(5)
    header = get_header()
    status_code = 0
    try:
        response = requests.get(full_url, proxies=proxy, timeout=time, headers=header)
        status_code = response.status_code
        print(response.status_code, url)
    except RequestException as ex:
        print(url + ":", ex)
        logging.error(ex)
        pass

    tcpdump.kill()
    tcpdump.wait()
    file.write(str(status_code))
    file.close()
    # change_exit_node(port)


def start_tor_process(torrc):
    print("Launching torrc." + torrc)
    return stem.process.launch_tor(torrc_path=torrc, timeout=120, take_ownership=True)


# Open a new circuit and get a new exit node, e.g. new IP address.
def change_exit_node(port):
    control_port = int(port) + 1
    with Controller.from_port(port=control_port) as controller:
        controller.authenticate()
        if controller.is_newnym_available():
            controller.signal(Signal.NEWNYM)
    sleep(5)


# Remove data directory to force tor to use new entry guards.
def change_entry_guard():
    for files in os.listdir(path_to_data_directory):
        path = os.path.join(path_to_data_directory, files)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)


# TODO: Change at home to all_websites and on HM to clean_websites
def get_new_url():
    return clean_websites[current_url_index % len(clean_websites)]


def get_new_port():
    return ports[current_port_index % max_tors]


def get_header():
    header = Headers(
        browser="firefox",
        os="random",
        headers=True  # generate misc headers
    )
    """
    full_url = "https://www." + url + "/"
    random_user_agents = ["Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
                          "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
                          "Mozilla/5.0 (Macintosh; Intel Mac OS X 12.1; rv:95.0) Gecko/20100101 Firefox/95.0",
                          "Mozilla/5.0 (X11; Linux i686; rv:95.0) Gecko/20100101 Firefox/95.0",
                          "Mozilla/5.0 (Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
                          "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:95.0) Gecko/20100101 Firefox/95.0",
                          "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
                          "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0"]

    headers = {
        "rokna.net": {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                      "Accept-Encoding": "gzip, deflate, br",
                      "Accept-Language": "en-US,en;q=0.5",
                      "Connection": "keep-alive",
                      "Host": "www.rokna.net",
                      "Origin": "https://www.rokna.net",
                      "Sec-Fetch-Dest": "document",
                      "Sec-Fetch-Mode": "navigate",
                      "Sec-Fetch-Site": "none",
                      "Sec-Fetch-User": "?1",
                      "Upgrade-Insecure-Requests": "1",
                      "User-Agent": random_user_agents[random.randint(0, 7)]
                      },
        "whatsapp.com": {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                         "Accept-Encoding": "gzip, deflate, br",
                         "Accept-Language": "en-US,en;q=0.5",
                         "Connection": "keep-alive",
                         "Host": "www.whatsapp.com",
                         "Sec-Fetch-Dest": "document",
                         "Sec-Fetch-Mode": "navigate",
                         "Sec-Fetch-Site": "none",
                         "Sec-Fetch-User": "?1",
                         "Upgrade-Insecure-Requests": "1",
                         "User-Agent": random_user_agents[random.randint(0, 7)]},
        "default": {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": random_user_agents[random.randrange(0, 7)],
                    "Referer": full_url, }}
    """
    return header.generate()


if __name__ == '__main__':
    logging.basicConfig(filename='example.log', level=logging.ERROR)
    clean_websites = ["linkedin.com", "gls-pakete.de", "instagram.com", "welt.de", "amazon.com", "varzesh3.com",
                      "youtube.com", "ebay.de", "wikipedia.org", "web.de", "aparat.com", "facebook.com", "filmix.ac",
                      "tiktok.com", "twitter.com", "netflix.com", "dhl.de", "mail.ru", "ok.ru", "t-online.de",
                      "yahoo.com", "bing.com", "vk.com", "whatsapp.com", "reddit.com", "live.com", "digikala.com",
                      "microsoft.com", "yandex.ru", "focus.de", "telewebion.com", "fandom.com", "spiegel.de", "chip.de",
                      "bild.de", "zalando.de", "n-tv.de", "msn.com", "paypal.com", "rokna.net", "telekom.com",
                      "tagesschau.de", "namasha.com", "google.com", "commerzbank.de", "zdf.de", "twitch.tv",
                      "wetter.com", "chefkoch.de"]  # 49

    dirty_websites = ["xvideos.com", "xnxx.com", "livejasmin.com"]  # 3

    # Dirty Websites are called two times at home because at HM it is not possible to generate this traffic and at
    # home clean Websites are also traced.
    all_websites = clean_websites + dirty_websites + dirty_websites

    ports = ["9150", "9250", "9350", "9450", "9550", "9650", "9750", "9850", "9950", "10050", "10150", "10250", "10350",
             "10450", "10550", "10650"]

    torrc_path = "/etc/tor/torrc."
    path_to_data_directory = "/home/ebse/Desktop/TorDataDirectory/"
    change_entry_guard()
    timeout = 180
    current_url_index = 0
    current_port_index = 0

    while True:
        max_tors = 8
        tor_processes = []
        fingerprint_processes = []
        for torrc_index in range(1, max_tors + 1):
            try:
                tor_processes.append(start_tor_process(torrc_path + str(torrc_index)))
            except OSError as error:
                print(error)
                max_tors -= 1

        for tor_index in range(max_tors):
            current_url = get_new_url()
            current_port = get_new_port()
            proxies = {
                'http': 'socks5://localhost:' + current_port,
                'https': 'socks5://localhost:' + current_port
            }
            fingerprint_processes.append(
                Process(target=create_fingerprint, args=(current_url, current_port, proxies, timeout)))
            current_url_index += 1
            current_port_index += 1

        # Run processes
        for process in fingerprint_processes:
            process.start()
        # Exit the completed processes
        for process in fingerprint_processes:
            process.join()

        # Kill tor processes
        for tor in tor_processes:
            tor.kill()
        for tor in tor_processes:
            tor.wait()

        change_entry_guard()
