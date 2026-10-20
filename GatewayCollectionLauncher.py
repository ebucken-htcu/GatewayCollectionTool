from datetime import datetime
from pathlib import Path
import hashlib
import subprocess
import json
import os
import requests
import shutil

VERSION_URL = "https://github.com/ebucken-htcu/GatewayCollectionTool/releases/latest/download/version.json"
MAIN_EXE_NAME = "GatewayCollectionTool.exe"


def hash(file_name):
    file_hash = ""
    try:
        with open(file_name, "rb") as file_stream:
            file_hash = hashlib.file_digest(file_stream, "sha256").hexdigest()
            print(f"The sha256 of {file_name} is {file_hash}")
            return(file_hash)
    except Exception as exception:
        print(f"Failed to hash {file_name}: {exception}")
        print("Update aborted!")
        return False


def get_github_hash():
    try:
        data = requests.get("https://github.com/ebucken-htcu/GatewayCollectionTool/releases/latest/version.json", 
                                timeout=30)
        version_json = data.json()
        return version_json["sha256"]
    except Exception as exception:
        print(f"Failed to retreive release hash: {exception}")
        print("Update aborted!")
        return False
    

def check_hashes(file_name):
    print(f"Verifying {file_name}...")
    local_hash = hash(file_name)
    if local_hash == False:
        return False
    
    remote_hash = get_github_hash()
    if remote_hash == False:
        return False
    elif local_hash == remote_hash:
        print("Download Verified!")
        return True
    elif remote_hash != local_hash:
        print(f"Downloaded hash does NOT match! Update aborted!")


def delete_file(file_name):
    try:
        file_path = Path(file_name)
        file_path.unlink(missing_ok=True)
    except Exception as exception:
        print(f"failed to delete file {file_name}: {exception}")


def copy_file(from_file, to_file):
    try:
        shutil.copyfile(from_file, to_file)
    except Exception as exception:
        print(f"Replacing file failed: {exception}")


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
                print(f"New Version {latest_version} found! Downloading...")
                update_app(download_url, latest_version) 
            else:
                print("Gateway Collection Tool is up to date!")
        elif (local_version == "0"):
            print(f"Downloading Latest release because version.json was missing...")
            update_app(download_url, latest_version)
        elif (local_version == "-1"):
            print(f"Downloading Latest release because version.json was invalid...")
            update_app(download_url, latest_version)

        return download_url
    except Exception as exception:
        print(f"Update failed or skipped: {exception}")
        print(f"Launching existing version")
        return "failed to get download_url"


def update_app(download_url, latest_version):
    
    exe_response = requests.get(download_url, timeout=30)
    exe_response.raise_for_status()
    temp_exe = f"{MAIN_EXE_NAME}.temp"

    try:
        with open(temp_exe, "wb") as file_stream:
            file_stream.write(exe_response.content)
    except Exception as exception:
        print(f"failed to download new {MAIN_EXE_NAME}: {exception}")

    if (check_hashes(temp_exe)):
        copy_file(temp_exe, MAIN_EXE_NAME)
        update_local_version(latest_version)
    delete_file(temp_exe)
    

def launch_app(download_url):
    if os.path.exists(MAIN_EXE_NAME):
        subprocess.Popen([MAIN_EXE_NAME])
        print("Launching Gateway Collection Tool!")
    else:
        print(f"Error: {MAIN_EXE_NAME} missing!")
        print(f"Downloading latest {MAIN_EXE_NAME}...")
        update_app(download_url)
        input("Please relaunch. Press Enter to Continue...")

if __name__ == "__main__":
    download_url = check_for_update()
    launch_app(download_url)