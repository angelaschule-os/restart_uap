#!/usr/bin/env python3

import os
import requests
import logging
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Disable SSL certificate warnings
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

disable_warnings(InsecureRequestWarning)


def setup_logging():
    logger = logging.getLogger("requests")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


def filter_mac_addresses(json_data):
    mac_addresses = []
    for device in json_data["data"]:
        if device["type"] == "uap":
            mac_addresses.append(device["mac"])
    return mac_addresses


def load_credentials():
    load_dotenv()

    username = os.getenv("API_USERNAME")
    password = os.getenv("API_PASSWORD")
    base_url = os.getenv("API_BASE_URL")

    return username, password, base_url


def login(base_url, username, password, session, logger):
    login_url = f"{base_url}/api/login"
    login_data = {"username": username, "password": password, "remember": True}

    try:
        login_response = session.post(login_url, json=login_data, verify=False)
    except requests.exceptions.RequestException as e:
        logger.error("Login request failed: %s", e)
        return False

    return login_response.status_code == 200


def fetch_data(base_url, session, logger):
    data_url = f"{base_url}/api/s/default/stat/device-basic"

    try:
        response = session.get(data_url, verify=False)
    except requests.exceptions.RequestException as e:
        logger.error("Request failed: %s", e)
        return None

    if response.status_code == 200:
        return response.json()
    else:
        logger.error(
            "Failed to fetch data from URL. Status code: %d", response.status_code
        )
        return None


def restart_device(base_url, mac_address, session, logger):
    cmd_url = f"{base_url}/api/s/default/cmd/devmgr"
    post_data = {"cmd": "restart", "mac": mac_address}

    try:
        cmd_response = session.post(cmd_url, json=post_data, verify=False)
    except requests.exceptions.RequestException as e:
        logger.error("Request failed for MAC address %s: %s", mac_address, e)
        return False

    if cmd_response.status_code == 200:
        return True
    else:
        logger.error(
            "Failed to restart device with MAC address %s. Status code: %d",
            mac_address,
            cmd_response.status_code,
        )
        return False


def restart_device_wrapper(args):
    base_url, mac_address, session, logger = args
    return mac_address, restart_device(base_url, mac_address, session, logger)


def main():
    logger = setup_logging()
    username, password, base_url = load_credentials()

    with requests.Session() as session:
        if login(base_url, username, password, session, logger):
            json_data = fetch_data(base_url, session, logger)

            if json_data:
                mac_addresses = filter_mac_addresses(json_data)
                print("Filtered MAC addresses:", mac_addresses)

                with ThreadPoolExecutor(max_workers=20) as executor:
                    futures = [
                        executor.submit(
                            restart_device_wrapper,
                            (base_url, mac, session, logger),
                        )
                        for mac in mac_addresses
                    ]

                for future in as_completed(futures):
                    mac_address, success = future.result()
                    if success:
                        print(
                            f"Successfully restarted device with MAC address {mac_address}"
                        )
                    else:
                        print(
                            f"Failed to restart device with MAC address {mac_address}"
                        )

            else:
                print("Failed to fetch data from URL")
        else:
            print("Login failed")


if __name__ == "__main__":
    main()
