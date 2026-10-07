#!/bin/bash

# Gateway IR WSL Mode 1
# Read-only targeted gateway interrogation
# Usage:
# ./GatewayIR_WSL_Mode1.sh <gateway_ip> <subnet>
#
# Example:
# ./GatewayIR_WSL_Mode1.sh 10.0.0.1 10.0.0.0/24

GATEWAY="$1"
SUBNET="$2"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BASE_DIR="/mnt/c/Gateway IR/Gateway_IR_${TIMESTAMP}"
OUTDIR="${BASE_DIR}/WSL"

mkdir -p "$OUTDIR"

echo "[+] Gateway IR WSL Mode 1"
echo "[+] Gateway: $GATEWAY"
echo "[+] Subnet: $SUBNET"
echo "[+] Output: $OUTDIR"

if [ -z "$GATEWAY" ] || [ -z "$SUBNET" ]; then
    echo "[!] Usage: ./GatewayIR_WSL_Mode1.sh <gateway_ip> <subnet>"
    exit 1
fi

# System documentation
date > "$OUTDIR/date.txt"
timedatectl > "$OUTDIR/timedatectl.txt" 2>&1
uname -a > "$OUTDIR/uname.txt"
ip addr > "$OUTDIR/wsl_ip_addr.txt"
ip route > "$OUTDIR/wsl_ip_route.txt"
cat /etc/resolv.conf > "$OUTDIR/wsl_resolv_conf.txt" 2>&1

# Gateway checks
ping -c 4 "$GATEWAY" > "$OUTDIR/gateway_ping.txt" 2>&1

curl -I "http://$GATEWAY" > "$OUTDIR/gateway_http_headers.txt" 2>&1
curl -k -I "https://$GATEWAY" > "$OUTDIR/gateway_https_headers.txt" 2>&1
curl "http://$GATEWAY" > "$OUTDIR/gateway_http_index.html" 2>&1

openssl s_client -connect "$GATEWAY:443" < /dev/null > "$OUTDIR/gateway_ssl_info.txt" 2>&1

# Targeted Nmap scans
if command -v nmap >/dev/null 2>&1; then
    nmap -sV "$GATEWAY" -oA "$OUTDIR/nmap_gateway_services" > "$OUTDIR/nmap_gateway_services_console.txt" 2>&1
    nmap -O "$GATEWAY" -oA "$OUTDIR/nmap_gateway_os" > "$OUTDIR/nmap_gateway_os_console.txt" 2>&1
    nmap -sn "$SUBNET" -oA "$OUTDIR/nmap_visible_hosts" > "$OUTDIR/nmap_visible_hosts_console.txt" 2>&1
    nmap -sU -p161 "$GATEWAY" -oA "$OUTDIR/nmap_gateway_snmp" > "$OUTDIR/nmap_gateway_snmp_console.txt" 2>&1
else
    echo "nmap not installed" > "$OUTDIR/nmap_status.txt"
fi

# UPnP discovery
if command -v upnpc >/dev/null 2>&1; then
    upnpc -l > "$OUTDIR/upnp_port_mappings.txt" 2>&1
else
    echo "miniupnpc/upnpc not installed" > "$OUTDIR/upnp_status.txt"
fi

# mDNS discovery
if command -v avahi-browse >/dev/null 2>&1; then
    timeout 45 avahi-browse -at > "$OUTDIR/mdns_avahi_browse.txt" 2>&1
else
    echo "avahi-browse not installed" > "$OUTDIR/mdns_status.txt"
fi

# NetBIOS scan with nmblookup if available
if command -v nmblookup >/dev/null 2>&1; then
    nmblookup -A "$GATEWAY" > "$OUTDIR/netbios_gateway.txt" 2>&1
else
    echo "nmblookup not installed" > "$OUTDIR/netbios_status.txt"
fi

# Automated keyword review
COMBINED="$OUTDIR/combined_wsl_text.txt"
cat "$OUTDIR"/*.txt "$OUTDIR"/*.nmap "$OUTDIR"/*.gnmap 2>/dev/null > "$COMBINED"

grep -iE "blink|ring|arlo|nest|reolink|lorex|hikvision|dahua|camera|cam|nvr|dvr" "$COMBINED" > "$OUTDIR/potential_cameras.txt" 2>/dev/null
grep -iE "iphone|ipad|android|samsung|pixel|motorola|oneplus|galaxy" "$COMBINED" > "$OUTDIR/potential_mobile_devices.txt" 2>/dev/null
grep -iE "synology|qnap|nas|wdmycloud|mycloud|seagate|storage" "$COMBINED" > "$OUTDIR/potential_storage_devices.txt" 2>/dev/null
grep -iE "xbox|playstation|ps4|ps5|nintendo|switch|roku|firetv|chromecast|appletv" "$COMBINED" > "$OUTDIR/potential_gaming_streaming.txt" 2>/dev/null
grep -iE "ssh|telnet|rdp|3389|vnc|5900|upnp|openvpn|wireguard|ipsec|tailscale|zerotier" "$COMBINED" > "$OUTDIR/potential_remote_access_vpn.txt" 2>/dev/null

# Summary
SUMMARY="$OUTDIR/GATEWAY_IR_WSL_SUMMARY.txt"

cat > "$SUMMARY" << EOF
=========================================
GATEWAY IR WSL MODE 1 SUMMARY
=========================================

Collection Date:
$(date)

Mode:
Read-only WSL targeted gateway interrogation

Gateway:
$GATEWAY

Subnet:
$SUBNET

Output Folder:
$OUTDIR

-----------------------------------------
WHAT THIS SCRIPT COLLECTED
-----------------------------------------
- WSL system time
- WSL network configuration
- Gateway ping
- Gateway HTTP headers
- Gateway HTTPS headers
- Gateway SSL certificate information
- Gateway service scan
- Gateway OS scan
- Visible host scan against Windows-provided subnet
- SNMP check
- UPnP mapping check
- mDNS discovery
- NetBIOS gateway check
- Keyword review for cameras, phones, NAS, gaming, remote access, VPN

-----------------------------------------
POTENTIAL CAMERAS / DVR / NVR
-----------------------------------------
$(cat "$OUTDIR/potential_cameras.txt" 2>/dev/null || echo "None identified.")

-----------------------------------------
POTENTIAL MOBILE DEVICES
-----------------------------------------
$(cat "$OUTDIR/potential_mobile_devices.txt" 2>/dev/null || echo "None identified.")

-----------------------------------------
POTENTIAL STORAGE / NAS DEVICES
-----------------------------------------
$(cat "$OUTDIR/potential_storage_devices.txt" 2>/dev/null || echo "None identified.")

-----------------------------------------
POTENTIAL GAMING / STREAMING DEVICES
-----------------------------------------
$(cat "$OUTDIR/potential_gaming_streaming.txt" 2>/dev/null || echo "None identified.")

-----------------------------------------
POTENTIAL REMOTE ACCESS / VPN INDICATORS
-----------------------------------------
$(cat "$OUTDIR/potential_remote_access_vpn.txt" 2>/dev/null || echo "None identified.")

-----------------------------------------
IMPORTANT LIMITATION
-----------------------------------------
This script does not log into the gateway.

This script does not collect:
- Historical devices
- Offline devices
- DHCP history
- Wireless client history
- Xfinity account information
- Gateway logs
- Gateway configuration backup

Those require gateway login, export, screenshots, provider portal access, consent, or legal process.

=========================================
EOF

# Hash outputs
find "$OUTDIR" -type f ! -name "SHA256SUMS.txt" -exec sha256sum {} \; > "$OUTDIR/SHA256SUMS.txt"

echo "[+] WSL collection complete."
echo "[+] Summary: $SUMMARY"
echo "[+] Hashes: $OUTDIR/SHA256SUMS.txt"