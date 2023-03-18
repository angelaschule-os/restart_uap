#!/usr/bin/env python3

import os
import requests
import json
import logging
from dotenv import load_dotenv


def setup_logging():
    # Create a custom logger
    logger = logging.getLogger("requests")
    logger.setLevel(logging.DEBUG)

    # Create a console handler to print logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(console_handler)

    return logger


def filter_mac_addresses(json_data):
    mac_addresses = []
    for device in json_data["data"]:
        if device["type"] == "uap":
            mac_addresses.append(device["mac"])
    return mac_addresses


def main():
    logger = setup_logging()

    # Load the .env file
    load_dotenv()

    # Get the username and password from the environment variables
    username = os.getenv("API_USERNAME")
    password = os.getenv("API_PASSWORD")
    base_url = os.getenv("API_BASE_URL")

    login_url = f"{base_url}/api/login"
    data_url = f"{base_url}/api/s/default/stat/device-basic"
    cmd_url = f"{base_url}/api/s/default/cmd/devmgr"

    # Prepare the login data
    login_data = {"username": username, "password": password, "remember": True}

    # Send a POST request to the login API
    try:
        login_response = requests.post(login_url, json=login_data, verify=False)
    except requests.exceptions.RequestException as e:
        logger.error("Login request failed: %s", e)
        return

    # Check if the login was successful
    if login_response.status_code == 200:
        # Get the session cookie
        session_cookie = login_response.cookies

        # Use the session cookie to authenticate subsequent requests
        try:
            response = requests.get(data_url, cookies=session_cookie, verify=False)
        except requests.exceptions.RequestException as e:
            logger.error("Request failed: %s", e)
            return

        if response.status_code == 200:
            json_data = response.json()
            mac_addresses = filter_mac_addresses(json_data)
            print("Filtered MAC addresses:", mac_addresses)

            # Send a POST request for each MAC address
            for mac_address in mac_addresses:
                post_data = {"cmd": "restart", "mac": mac_address}

                try:
                    cmd_response = requests.post(
                        cmd_url, json=post_data, cookies=session_cookie, verify=False
                    )
                except requests.exceptions.RequestException as e:
                    logger.error(
                        "Request failed for MAC address %s: %s", mac_address, e
                    )
                    continue

                if cmd_response.status_code == 200:
                    print(
                        f"Successfully restarted device with MAC address {mac_address}"
                    )
                else:
                    print(f"Failed to restart device with MAC address {mac_address}")
                    logger.error(
                        "Failed to restart device with MAC address %s. Status code: %d",
                        mac_address,
                        cmd_response.status_code,
                    )

        else:
            print("Failed to fetch data from URL")
            logger.error(
                "Failed to fetch data from URL. Status code: %d", response.status_code
            )
    else:
        print("Login failed")
        logger.error("Login failed. Status code: %d", login_response.status_code)


if __name__ == "__main__":
    main()
