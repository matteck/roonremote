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

server = "192.168.50.125"
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

api = roonapi.RoonApi(appinfo, token, server)

with open(token_file, "w") as f:
    f.write(api.token)

zones = api.zones
# Attach to currently playing zone, or arbitrarily choose last if nothing is playing
zones = api.zones
for output in zones.values():
    output_id = output["zone_id"]
    if output['state'] == "playing":
        break
print(output_id)

devices = {}
for fn in evdev.list_devices():
    print(fn)
    dev = evdev.InputDevice(fn)
    devices[dev.fd] = dev
print(devices)
while True:
    r, w, x = select.select(devices, [], [])
    for fd in r:
        for event in devices[fd].read():
            if event.type == evdev.ecodes.EV_KEY:
                keyev = evdev.categorize(event)
                code = keyev.keycode[4:]
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
                        api.playback_control(output_id, "playpause")
                    elif code == "STOP":
                        # Stop all playback
                        zones = api.zones
                        for output in zones.values():
                            output_id = output["zone_id"]
                            api.playback_control(output_id, "stop")
                    elif code == "REWIND":
                        api.playback_control(output_id, "previous")
                    elif code == "FASTFORWARD":
                        api.playback_control(output_id, "next")
                    elif code == "INFO":
                        # Attach to currently playing zone, or no change if nothing is playing
                        zones = api.zones
                        for output in zones.values():
                            if output['state'] == "playing":
                                output_id = output["zone_id"]
                                #print(output_id)
                                break
