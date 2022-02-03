#!/usr/bin/env python3

# Shut down 5 minutes after DAC is disconnected

import subprocess
from pathlib import Path
import time
from os import path

card = '/proc/asound/card1/stream0'
flag_file = "/root/.roon_playing_flag"
shutdown_delay_min = 5

flag_path = Path(flag_file)

if path.exists("/proc/asound/card1/stream0") == True:
    #print("DAC is on")
    flag_path.touch()
else:
    try:
        # get ctime
        ctime = flag_path.stat().st_ctime
    except FileNotFoundError:
        # print("Flag file not found. Creating ", flag_file)
        flag_path.touch()
    else:
        if ctime < time.time() - shutdown_delay_min * 60:
            # print("Shutting down PortPi")
            flag_path.unlink()
            subprocess.run(['/sbin/shutdown','-P','now'])
