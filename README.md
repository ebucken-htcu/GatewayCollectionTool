# Gateway Collection Tool
## Description
This is a Digital Forensics and Incident Response tool that you can run to collect information from a router on scene. Currently there is only a mode to collect information from residential home networks. Only works on x64 windows machines.
### Setup Instructions
1. download the latest file
    - GatewayCollectionLauncher.exe
2. Download and install Nmap and Npcap these are dependencies
3. Run
    - Run GatewayCollectionLauncher.exe it will auto update the script on launch if new functionality has been added
    - ONLY run GatewayCollectionTool.exe if you eiter know you have no internet connection or do not intend to update the script currently
### Notes
- the three files must be in the same directory on your system, if do not have version.json or GatewayCollectionTool.exe, the Launcher will automaticaly try to download the latest version
- the tool can be ran without Nmap and Npcap, it will skip over those parts if it doesnt find the dependencies
### Update Plans
- Buisness collection mode
- auto-generating a pdf report with all the information at the end
- some sort of display to show how far the script is through its collection or a spinning wheel to remind people it is still running
