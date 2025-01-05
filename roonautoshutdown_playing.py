#!/usr/bin/env python3

import subprocess
from pathlib import Path
import time

card = '/proc/asound/card1/stream0'
flag_file = "/tmp/roon_playing_flag"
shutdown_delay_min = 60

with open('/proc/sys/kernel/random/boot_id') as f:
    boot_id = f.read().strip()

flag_path = Path(flag_file + '-' + boot_id)

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
        if ctime < time.time() - (shutdown_delay_min + 15) * 60:
            # Flag file expired more than 15 minutes ago, should have already been deleted by auto shutdown if cron job worked, is now stale
            flag_path.unlink()
        elif ctime < time.time() - shutdown_delay_min * 60:
            # print("Shutting down PortPi")
            flag_path.unlink()
            subprocess.run(['/sbin/shutdown','-P','now'])
