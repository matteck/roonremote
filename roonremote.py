#!/usr/bin/env python3

# Codes:
# BACK
# CONTEXT_MENU
# DOWN
# ENTER
# FASTFORWARD
# HOME
# INFO
# LEFT
# PLAYPAUSE
# REWIND
# RIGHT
# STOP
# UP

import evdev
import select
import roonapi
import subprocess

# TODO
# - Discover server
# - Set zone in extension prefences
# - Seek within track

host = "192.168.50.125"
port = 9330
zone_name = "iFi"
token_file = "/root/.roon_token_save"

appinfo = {
    "extension_id": "roonremote",
    "display_name": "Remote control with OSMC remote",
    "display_version": "0.0.1",
    "publisher": "Matthew Eckhaus",
    "email": "matteck@github",
}

# Can be None if you don't yet have a token
try:
    token = open(token_file).read()
except FileNotFoundError:
    token = None

api = roonapi.RoonApi(appinfo, token, host, port)

with open(token_file, "w") as f:
    f.write(api.token)

zones = api.zones
# Attach to currently playing zone, or arbitrarily choose last if nothing is playing
for zone in zones.values():
    zone_id = zone["zone_id"]
    if zone['state'] == "playing":
        break
print("Here 1", zone_id)
print("here 2", zone['outputs'])

devices = {}
for fn in evdev.list_devices():
    print(fn)
    dev = evdev.InputDevice(fn)
    devices[dev.fd] = dev
print(devices)

def vol_change(incr):
    outputs = zone['outputs']
    for output in outputs:
        if 'volume' in output:
            output_id = output['output_id']
            print("Doing vol change")
            api.change_volume_raw(output_id, incr, 'relative')
            print("Done vol change")

while True:
    r, w, x = select.select(devices, [], [])
    for fd in r:
        for event in devices[fd].read():
            if event.type == evdev.ecodes.EV_KEY:
                keyev = evdev.categorize(event)
                code = keyev.keycode[4:]
                print(code)
                state = keyev.keystate
                if state == evdev.events.KeyEvent.key_down:
                    state = "DOWN"
                elif state == evdev.events.KeyEvent.key_up:
                    state = "UP"
                elif state == evdev.events.KeyEvent.key_hold:
                    state = "HOLD"
                #print(code, state)
                if state == "DOWN":
                    if code == "HOME":
                        subprocess.run(['ssh', '-i', '/root/.ssh/id_auto_home', 'root@portpi', 'shutdown -P now'])
                    if code == "PLAYPAUSE":
                        api.playback_control(zone_id, "playpause")
                    elif code == "STOP":
                        # Stop all playback
                        zones = api.zones
                        for zone in zones.values():
                            zone_id2 = output["zone_id"]
                            api.playback_control(zone_id2, "stop")
                    elif code == "REWIND":
                        api.playback_control(zone_id, "previous")
                    elif code == "FASTFORWARD":
                        api.playback_control(zone_id, "next")
                    elif code == "INFO":
                        # Attach to currently playing zone, or no change if nothing is playing
                        zones = api.zones
                        for zone in zones.values():
                            if zone['state'] == "playing":
                                zone_id = zone["zone_id"]
                                print(zone_id)
                                break
                    elif code == "DOWN":
                        vol_change(-1)
                    elif code == "UP":
                        vol_change(1)
