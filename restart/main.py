#!/usr/bin/env python3

import os
import requests
import json
import logging
from dotenv import load_dotenv


def setup_logging():
    logger = logging.getLogger("requests")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
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


def login(base_url, username, password):
    login_url = f"{base_url}/api/login"
    login_data = {"username": username, "password": password, "remember": True}

    try:
        login_response = requests.post(login_url, json=login_data, verify=False)
    except requests.exceptions.RequestException as e:
        logger.error("Login request failed: %s", e)
        return None

    if login_response.status_code == 200:
        return login_response.cookies
    else:
        logger.error("Login failed. Status code: %d", login_response.status_code)
        return None


def fetch_data(base_url, session_cookie):
    data_url = f"{base_url}/api/s/default/stat/device-basic"

    try:
        response = requests.get(data_url, cookies=session_cookie, verify=False)
    except requests.exceptions.RequestException as e:
        logger.error("Request failed: %s", e)
        return None

    if response.status_code == 200:
        return response.json()
    else:
        logger.error("Failed to fetch data from URL. Status code: %d", response.status_code)
        return None


def restart_device(base_url, mac_address, session_cookie):
    cmd_url = f"{base_url}/api/s/default/cmd/devmgr"
    post_data = {"cmd": "restart", "mac": mac_address}

    try:
        cmd_response = requests.post(cmd_url, json=post_data, cookies=session_cookie, verify=False)
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


def main():
    global logger
    logger = setup_logging()

    username, password, base_url = load_credentials()
    session_cookie = login(base_url, username, password)

    if session_cookie:
        json_data = fetch_data(base_url, session_cookie)

        if json_data:
            mac_addresses = filter_mac_addresses(json_data)
            print("Filtered MAC addresses:", mac_addresses)

            for mac_address in mac_addresses:
                if restart_device(base_url, mac_address, session_cookie):
                    print(f"Successfully restarted device with MAC address {mac_address}")
                else:
                    print(f"Failed to restart device with MAC address {mac_address}")
        else:
            print("Failed to fetch data from URL")
    else:
        print("Login failed")


if __name__ == "__main__":
    main()
