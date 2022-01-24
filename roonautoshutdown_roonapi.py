#!/usr/bin/env python3

import roonapi
import subprocess
from pathlib import Path
import time
import logging

host = "192.168.50.125"
port = 9330
zone_name = "iFi"
token_file = "/root/.roon_token_save"
flag_file = "/root/.roon_playing_flag"
shutdown_delay_min = 60
this_zone_name = "iFi"

appinfo = {
    "extension_id": "roonshutdown",
    "display_name": "Auto shutdown host when roon not playing",
    "display_version": "0.0.1",
    "publisher": "Matthew Eckhaus",
    "email": "matteck@github",
}

flag_path = Path(flag_file)

# Can be None if you don't yet have a token
try:
    token = open(token_file).read()
except FileNotFoundError:
    token = None

roonapi.LOGGER.setLevel(logging.WARN)
#print("connecting to server")
api = roonapi.RoonApi(appinfo, token, host, port)

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
    flag_path.touch()
else:
    try:
        # get ctime
        ctime = flag_path.stat().st_ctime
    except FileNotFoundError:
        #print("Flag file not found. Creating ", flag_file)
        flag_path.touch()
    else:
        if ctime < time.time() - shutdown_delay_min * 60:
            print("Shutting down PortPi")
            flag_path.unlink()
            subprocess.run(['/sbin/shutdown','-P','now'])
