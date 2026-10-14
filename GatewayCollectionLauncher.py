from datetime import datetime
import subprocess
import sys
import os
import requests

CURRENT_VERSION = "0.2.0"
VERSION_URL = ""
MAIN_EXE_NAME = ""

last_attempted_update = ""

def check_for_update():
    print("checking for updates...")
    try:
        response = requests.get(VERSION_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        latest_version = data["version"]
        download_url = data["download_url"]

        if (latest_version > CURRENT_VERSION):
            update_app(latest_version, download_url)
    except Exception as exception:
        print(f"Update failed or skipped: {exception}")
        print(f"Launching existing version")


def update_app(latest_version, download_url):
    print(f"New Version {latest_version} found! Downloading!=...")
    
    exe_response = requests.get(download_url, timeout=30)
    exe_response.raise_for_status()

    with open(MAIN_EXE_NAME, "wb") as file_stream:
        file_stream.write(exe_response.content)

    print("Update Complete!")
    print("Launching New Version!")

def launch_app():
    subprocess.run([sys.executable])

if __name__ == "__main__":
    check_for_update()
    launch_app()