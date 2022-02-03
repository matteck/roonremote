#!/usr/bin/env python3

import subprocess
from pathlib import Path
import time

card = '/proc/asound/card1/stream0'
flag_file = "/root/.roon_playing_flag"
shutdown_delay_min = 20

flag_path = Path(flag_file)

completed_process  = subprocess.run(["grep", "-i", "Status: Running", card], capture_output=True)
if completed_process.returncode == 0:
    #print("Playing")
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
