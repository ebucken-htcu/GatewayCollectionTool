from datetime import datetime
import subprocess
import json
import os
import requests

VERSION_URL = "https://github.com/ebucken-htcu/GatewayCollectionTool/releases/latest/download/version.json"
MAIN_EXE_NAME = "GatewayCollectionTool.exe"


def update_local_version(new_version):
    try:
        with open('version.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        data["version"] = new_version
        with open('version.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
    except FileNotFoundError:
        print("Error: the file version.json is missing!")
    except json.JSONDecodeError:
        print("Error: version.json contains invalid JSON syntax!")


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
                update_local_version(latest_version)
            else:
                print("Gateway Collection Tool is up to date!")
    except Exception as exception:
        print(f"Update failed or skipped: {exception}")
        print(f"Launching existing version")


def update_app(latest_version, download_url):
    print(f"New Version {latest_version} found! Downloading...")
    
    exe_response = requests.get(download_url, timeout=30)
    exe_response.raise_for_status()

    try:
        with open(MAIN_EXE_NAME, "wb") as file_stream:
            file_stream.write(exe_response.content)
    except Exception as exception:
        print(f"failed to update {MAIN_EXE_NAME}: {exception}")

    print("Update Complete!")

def launch_app():
    if os.path.exists(MAIN_EXE_NAME):
        subprocess.Popen([MAIN_EXE_NAME])
        print("Launching New Version!")
    else:
        print(f"Critical error: {MAIN_EXE_NAME} missing!")
        input("Press Enter to exit...")

if __name__ == "__main__":
    check_for_update()
    launch_app()