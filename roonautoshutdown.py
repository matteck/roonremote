#!/usr/bin/env python3

import roonapi
import subprocess
from pathlib import Path
import time
import logging

server = "192.168.50.125"
zone_name = "iFi"
token_file = "/root/.roon_token_save"
flag_file = "/root/.roon_playing_flag"
shutdown_delay_min = 10
this_zone_name = "iFi"

appinfo = {
    "extension_id": "roonshutdown",
    "display_name": "Auto shutdown host when roon not playing",
    "display_version": "0.0.1",
    "publisher": "Matthew Eckhaus",
    "email": "matteck@github",
}

# Can be None if you don't yet have a token
try:
    token = open(token_file).read()
except FileNotFoundError:
    token = None

roonapi.LOGGER.setLevel(logging.WARN)
api = roonapi.RoonApi(appinfo, token, server)

with open(token_file, "w") as f:
    f.write(api.token)


zones = api.zones
playing = False
for output in zones.values():
    if this_zone_name in output['display_name']:
        if output['state'] == "playing":
            playing = True
            break

if playing == True:
    with open(flag_file, "w") as f:
        f.write(str(int(time.time())))
        print("Playing. Writing ", str(int(time.time())))
else:
    try:
        with open(flag_file, "r") as f:
            timestamp = int(f.read())
        if timestamp < time.time() - shutdown_delay_min * 60:
            subprocess.run(['shutdown','-P','now'])
            print("Shutting down PortPi")
        else:
            print("Nimer not expired")
    except FileNotFoundError:
        with open(flag_file, "w") as f:
            f.write(str(int(time.time())))
            print("No file. Writing ", str(int(time.time())))
