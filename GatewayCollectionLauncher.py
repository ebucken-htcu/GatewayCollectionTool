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
        print("Downloading new version.json...")
        exe_response = requests.get(VERSION_URL, timeout=30)
        exe_response.raise_for_status()
        
        try:
            with open("version.json", "wb") as file_stream:
                file_stream.write(exe_response.content)
        except Exception as exception:
            print(f"failed to download new version.json: {exception}")
        
        return "0"
    except json.JSONDecodeError:
        print("Error: the file version.json has Syntax errors!")
        print("Downloading new version.json...")
        exe_response = requests.get(VERSION_URL, timeout=30)
        exe_response.raise_for_status()
        
        try:
            with open("version.json", "wb") as file_stream:
                file_stream.write(exe_response.content)
        except Exception as exception:
            print(f"failed to download new version.json: {exception}")
        return "-1"


def check_for_update():
    print("checking latest version...")
    try:
        response = requests.get(VERSION_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        latest_version = data["version"]
        download_url = data["download_url"]

        local_version = get_local_version()

        if (local_version > "0"):
            if (latest_version > local_version):
                update_app(download_url)
                update_local_version(latest_version)
                print(f"New Version {latest_version} found! Downloading...") 
            else:
                print("Gateway Collection Tool is up to date!")
        elif (local_version == "0"):
            print(f"Downloading Latest release because version.json was missing...")
            update_local_version(latest_version)
            update_app(download_url)
        elif (local_version == "-1"):
            print(f"Downloading Latest release because version.json was invalid...")
            update_local_version(latest_version)
            update_app(download_url)

        return download_url
    except Exception as exception:
        print(f"Update failed or skipped: {exception}")
        print(f"Launching existing version")
        return "failed to get download_url"


def update_app(download_url):
    
    exe_response = requests.get(download_url, timeout=30)
    exe_response.raise_for_status()

    try:
        with open(MAIN_EXE_NAME, "wb") as file_stream:
            file_stream.write(exe_response.content)
    except Exception as exception:
        print(f"failed to update {MAIN_EXE_NAME}: {exception}")

    print("Update Complete!")

def launch_app(download_url):
    if os.path.exists(MAIN_EXE_NAME):
        subprocess.Popen([MAIN_EXE_NAME])
        print("Launching New Version!")
    else:
        print(f"Error: {MAIN_EXE_NAME} missing!")
        print(f"Downloading latest {MAIN_EXE_NAME}...")
        update_app(download_url)
        input("Please relaunch. Press Enter to Continue...")

if __name__ == "__main__":
    download_url = check_for_update()
    launch_app(download_url)