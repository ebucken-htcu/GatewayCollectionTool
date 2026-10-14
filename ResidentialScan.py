import subprocess
import hashlib
import platform
import ipaddress
import re
from pathlib import Path
from datetime import datetime

case_number = "-1"
path = "\\"
agency = ""
analyst = ""

def set_case_number(number):
    global case_number
    case_number = number

def set_path(location):
    global path
    path = location

def set_agency(name):
    global agency
    agency = name

def set_analyst(name):
    global analyst
    analyst = name

def run_command(command, output_file, timeout=300):
    with open(output_file, "w", encoding="utf-8", errors="ignore") as file_stream:
        file_stream.write(f"COMMAND RUN: {command}\n")
        file_stream.write("=" * 80 + "\n\n")

        try:
            result = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True,
                timeout=timeout
            )

            file_stream.write(result.stdout)

            if result.stderr:
                file_stream.write("\n\nSTDERR:\n")
                file_stream.write(result.stderr)

            return result.stdout

        except Exception as exception:
            file_stream.write(f"ERROR: {exception}\n")
            return ""


def sha256_file(path):
    hash = hashlib.sha256()

    with open(path, "rb") as file_stream:
        for chunk in iter(lambda: file_stream.read(8192), b""):
            hash.update(chunk)

    return hash.hexdigest()


def find_nmap():
    possible_paths = [
        r"C:\Program Files (x86)\Nmap\nmap.exe",
        r"C:\Program Files\Nmap\nmap.exe",
        "nmap"
    ]

    for path in possible_paths:
        try:
            result = subprocess.run(
                f'"{path}" --version',
                shell=True,
                text=True,
                capture_output=True,
                timeout=10
            )

            if result.returncode == 0:
                return path
        except Exception:
            pass

    return None


def get_active_network():
    powershell_script = (
        "powershell -Command "
        "\"Get-NetIPConfiguration | "
        "Where-Object {$_.IPv4DefaultGateway -ne $null -and $_.IPv4Address -ne $null} | "
        "Select-Object -First 1 "
        "@{Name='InterfaceAlias';Expression={$_.InterfaceAlias}},"
        "@{Name='IPv4Address';Expression={$_.IPv4Address.IPAddress}},"
        "@{Name='PrefixLength';Expression={$_.IPv4Address.PrefixLength}},"
        "@{Name='Gateway';Expression={$_.IPv4DefaultGateway.NextHop}} | "
        "ConvertTo-Json\""
    )

    output = subprocess.run(
        powershell_script,
        shell=True,
        text=True,
        capture_output=True
    ).stdout

    gateway_match = re.search(r'"Gateway"\s*:\s*"([^"]+)"', output)
    ip_match = re.search(r'"IPv4Address"\s*:\s*"([^"]+)"', output)
    prefix_match = re.search(r'"PrefixLength"\s*:\s*(\d+)', output)
    interface_match = re.search(r'"InterfaceAlias"\s*:\s*"([^"]+)"', output)

    if not gateway_match or not ip_match or not prefix_match:
        return None

    ip_addr = ip_match.group(1)
    prefix = int(prefix_match.group(1))
    gateway = gateway_match.group(1)
    interface = interface_match.group(1) if interface_match else "Unknown"

    network = ipaddress.ip_network(f"{ip_addr}/{prefix}", strict=False)

    return {
        "interface": interface,
        "ip": ip_addr,
        "prefix": prefix,
        "gateway": gateway,
        "subnet": str(network)
    }


def classify_text(text):
    categories = {
        "Potential Cameras / DVR / NVR": [
            "blink", "ring", "arlo", "nest", "reolink", "lorex",
            "hikvision", "dahua", "camera", "cam", "nvr", "dvr"
        ],
        "Potential Mobile Devices": [
            "iphone", "ipad", "android", "samsung", "pixel",
            "motorola", "oneplus", "galaxy"
        ],
        "Potential Storage / NAS": [
            "synology", "qnap", "nas", "wdmycloud", "mycloud",
            "seagate", "storage", "ugreen", "unraid", "truenas"
        ],
        "Potential Gaming / Streaming": [
            "xbox", "playstation", "ps4", "ps5", "nintendo",
            "switch", "roku", "firetv", "chromecast", "appletv"
        ],
        "Potential Remote Access / VPN": [
            "ssh", "telnet", "rdp", "3389", "vnc", "5900",
            "upnp", "openvpn", "wireguard", "ipsec", "tailscale",
            "zerotier"
        ],
    }

    results = {}

    for category, terms in categories.items():
        hits = []
        for line in text.splitlines():
            lower = line.lower()
            if any(term in lower for term in terms):
                hits.append(line)

        results[category] = hits[:50]

    return results


def main(case_number, path, agency, analyst):
    set_case_number(case_number)
    set_path(path)
    set_agency(agency)
    set_analyst(analyst)

    scan_folder = Path(f"{path}\\{case_number}\\Residential_Mode_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    scan_folder = scan_folder / "Scans"

    scan_folder.mkdir(parents=True, exist_ok=True)

    print(f"[+] Scan folder created: {scan_folder}")

    active = get_active_network()

    if not active:
        print("[!] Could not identify active network.")
        return

    gateway = active["gateway"]
    subnet = active["subnet"]

    print(f"[+] Active interface: {active['interface']}")
    print(f"[+] Workstation IP: {active['ip']}/{active['prefix']}")
    print(f"[+] Gateway: {gateway}")
    print(f"[+] Subnet: {subnet}")

    windows_commands = {
        "date_time.txt": "powershell Get-Date",
        "connected_network_interface.txt": "netsh wlan show interfaces",
        "network_list.txt": "powershell Start-Process \"ms-availablenetworks:\"; Start-Sleep -Seconds 5; netsh wlan show networks mode=bssid",
        "get_net_connection_profile.txt": "powershell Get-NetConnectionProfile",
        "get_net_ip_configuration.txt": "powershell Get-NetIPConfiguration -Detailed",
        "get_net_neighbor.txt": "powershell -Command \"Get-NetNeighbor | Where-Object State -ne 'Unreachable'\"",
        "get_net_route.txt": "powershell Get-NetRoute",
        "gateway_ping.txt": f"ping {gateway}",
        "gateway_port_80.txt": f"powershell Test-NetConnection {gateway} -Port 80",
        "gateway_port_443.txt": f"powershell Test-NetConnection {gateway} -Port 443",
        "gateway_port_22.txt": f"powershell Test-NetConnection {gateway} -Port 22",
        "gateway_nslookup.txt": f"nslookup {gateway}",
    }

    for filename, command in windows_commands.items():
        print(f"[+] Windows: {command}")
        run_command(command, scan_folder / filename)

    nmap_path = find_nmap()

    if nmap_path:
        print(f"[+] Nmap found: {nmap_path}")

        nmap_commands = {
            "nmap_host_discovery.txt": f'"{nmap_path}" -sn {subnet}',
            "nmap_gateway_services.txt": f'"{nmap_path}" -sV {gateway}',
            "nmap_gateway_os.txt": f'"{nmap_path}" -O {gateway}',
        }

        for filename, command in nmap_commands.items():
            print(f"[+] Nmap: {command}")
            run_command(command, scan_folder / filename, timeout=600)
    else:
        print("[!] Nmap not found. Install Nmap for Windows.")
        (scan_folder / "nmap_status.txt").write_text(
            "Nmap was not found. Install Nmap for Windows.\n",
            encoding="utf-8"
        )

    combined_text = ""

    for file in scan_folder.rglob("*.txt"):
        try:
            combined_text += "\n\n" + file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            pass

    classifications = classify_text(combined_text)

    summary_file = "RESIDENTIAL_SCAN_SUMMARY.txt"

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("Residential Scan NETWORK INTELLIGENCE SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Collection Time: {datetime.now()}\n")
        f.write(f"Collection Laptop: {platform.node()}\n")
        f.write(f"Operating System: {platform.platform()}\n\n")

        f.write("NETWORK IDENTIFICATION\n")
        f.write("-" * 80 + "\n")
        f.write(f"Active Interface: {active['interface']}\n")
        f.write(f"Workstation IP: {active['ip']}/{active['prefix']}\n")
        f.write(f"Gateway: {gateway}\n")
        f.write(f"Subnet: {subnet}\n\n")

        f.write("Residential LIMITATION\n")
        f.write("-" * 80 + "\n")
        f.write("Residential script does not log into the gateway.\n")
        f.write("Residential script does not collect historical gateway logs.\n")
        f.write("Residential script does not collect ISP account information.\n")
        f.write("Residential script only identifies the gateway and currently visible network devices.\n\n")

        for category, hits in classifications.items():
            f.write(category.upper() + "\n")
            f.write("-" * 80 + "\n")

            if hits:
                for hit in hits:
                    f.write(hit + "\n")
            else:
                f.write("None identified from visible network scan.\n")

            f.write("\n")

        f.write("RECOMMENDED NEXT STEPS\n")
        f.write("-" * 80 + "\n")
        f.write("1. Open browser to the gateway.\n")
        f.write(f"   http://{gateway}\n")
        f.write(f"   https://{gateway}\n\n")
        f.write("2. Document gateway time, timezone, WAN IP, model, serial number, and firmware.\n")
        f.write("3. Export or screenshot current devices.\n")
        f.write("4. Export or screenshot offline/known devices.\n")
        f.write("5. Export DHCP history if available.\n")
        f.write("6. Export wireless client history if available.\n")
        f.write("7. Export router/gateway logs if available.\n")
        f.write("8. Export configuration backup if available.\n")
        f.write("9. Document cameras, NVRs, DVRs, NAS devices, and unknown mobile devices.\n")

    hash_file = "SHA256SUMS_CASE.txt"

    with open(hash_file, "w", encoding="utf-8") as f:
        for file in scan_folder.rglob("*"):
            if file.is_file() and file.name != "SHA256SUMS_CASE.txt":
                try:
                    f.write(f"{sha256_file(file)}  {file}\n")
                except Exception as e:
                    f.write(f"ERROR HASHING {file}: {e}\n")

    print("[+] Collection complete")
    print(f"[+] Summary: {summary_file}")
    print(f"[+] Hashes: {hash_file}")


if __name__ == "__main__":
    main(-1, "TestRuns", "test", "test")

