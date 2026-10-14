from datetime import datetime
import subprocess
import json
import os
import requests

VERSION_URL = "https://github.com/ebucken-htcu/GatewayCollectionTool/releases/latest/download/version.json"
MAIN_EXE_NAME = "GatewayCollectionTool.exe"


def get_local_version():
    try:
        with open('version.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            version = data["version"]
            print(f"Currently running version: {version}")
            return version
    except FileNotFoundError:
        print("Error: the file version.json is missing!")
        return -1
    except json.JSONDecodeError:
        print("Error: version.json contains invalid JSON syntax!")
        return -1


def check_for_update():
    print("checking for updates...")
    try:
        response = requests.get(VERSION_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        latest_version = data["version"]
        download_url = data["download_url"]

        local_version = get_local_version()

        if (local_version != -1):
            if (latest_version > local_version):
                update_app(latest_version, download_url)
            else:
                print("Gateway Collection Tool is up to date!")
    except Exception as exception:
        print(f"Update failed or skipped: {exception}")
        print(f"Launching existing version")


def update_app(latest_version, download_url):
    print(f"New Version {latest_version} found! Downloading...")
    
    exe_response = requests.get(download_url, timeout=30)
    exe_response.raise_for_status()

    with open(MAIN_EXE_NAME, "wb") as file_stream:
        file_stream.write(exe_response.content)

    print("Update Complete!")
    print("Launching New Version!")

def launch_app():
    if os.path.exists(MAIN_EXE_NAME):
        subprocess.Popen([MAIN_EXE_NAME])
    else:
        print(f"Critical error: {MAIN_EXE_NAME} missing!")
        input("Press Enter to exit...")

if __name__ == "__main__":
    check_for_update()
    launch_app()