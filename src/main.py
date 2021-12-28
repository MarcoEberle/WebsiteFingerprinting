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


# TODO: add https://askubuntu.com/questions/530920/tcpdump-permissions-problem
# sudo chgrp <user_running_this_code> /usr/sbin/tcpdump
# sudo chmod 750 /usr/sbin/tcpdump
def create_fingerprint(url, port, proxy):
    print("Creating Fingerprint of:", url, port)
    full_url = "https://www." + url + "/"
    timestamp = datetime.datetime.now().strftime("%d.%m_%H:%M:%S.%f")
    file = open("traces/" + timestamp + "_" + url + ".txt", "w")
    tcpdump = subprocess.Popen(['tcpdump', '-i', 'lo', '-n', '-vv', '-tttt', '-l', 'port', port], stdout=file)
    sleep(5)
    header = get_header()
    status_code = 0
    try:
        response = requests.get(full_url, proxies=proxy, headers=header)
        status_code = response.status_code
        status_logger.info(url + " : " + str(status_code))
        print(response.status_code, url)
        # print(requests.get("http://httpbin.org/ip", proxies=proxy, headers=header).text)
    except RequestException as ex:
        print(url + " : ", str(ex))
        error_logger.info(timestamp + " : " + url + " : " + str(ex))
        pass
    finally:
        tcpdump.kill()
        tcpdump.wait()
        file.write(str(status_code))
        file.close()

    try:
        change_exit_node(port)
    except Exception:
        pass


def start_tor_process(torrc):
    print("Launching: " + torrc)
    return stem.process.launch_tor(torrc_path=torrc, take_ownership=True)


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
    return header.generate()


if __name__ == '__main__':
    status_logger = logging.getLogger("status")
    error_logger = logging.getLogger("error")
    status_logger.setLevel(logging.INFO)
    error_logger.setLevel(logging.INFO)
    fh_status = logging.FileHandler("status.log", "a")
    status_logger.addHandler(fh_status)
    fh_error = logging.FileHandler("error.log", "a")
    error_logger.addHandler(fh_error)

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
        failed_tors = []
        tor_started = True

        for torrc_index in range(1, max_tors + 1):
            current_url = get_new_url()
            current_port = get_new_port()
            proxies = {
                'http': 'socks5://localhost:' + current_port,
                'https': 'socks5://localhost:' + current_port
            }
            try:
                # TODO: Parallel instead successively
                tor_processes.append(start_tor_process(torrc_path + str(torrc_index)))
            except OSError as error:
                print(error)
                error_logger.info("torrc." + str(torrc_index) + " : " + str(error))
                tor_started = False

            if tor_started:
                fingerprint_processes.append(
                    Process(target=create_fingerprint, args=(current_url, current_port, proxies)))
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
