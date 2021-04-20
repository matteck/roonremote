#!/usr/bin/env python3

import evdev
import select
import roonapi

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
output_id = [
    output["zone_id"]
    for output in zones.values()
    if output["display_name"] == zone_name
][0]
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
                print(code, state)
                if state == "DOWN":
                    if code == "PLAYPAUSE":
                        api.playback_control(output_id, "playpause")
                    elif code == "STOP":
                        api.playback_control(output_id, "stop")
                    elif code == "REWIND":
                        api.playback_control(output_id, "previous")
                    elif code == "FASTFORWARD":
                        api.playback_control(output_id, "next")
                    #elif code == "INFO":
                        #method = "POST"
                        #url = "%s/mute" % harmony_base_url
                #if state == "HOLD" or state == "DOWN":
                    #if code == "UP":
                        #method = "POST"
                        #url = "%s/volume-up" % harmony_base_url
                    #elif code == "DOWN":
                        #method = "POST"
                        #url = "%s/volume-down" % harmony_base_url
