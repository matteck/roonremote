#!/usr/bin/env python3

#TODO: find out default zone from roonrest and set volume/mute accordingly

import evdev
import select
import requests
import subprocess


roon_base_url = "http://roonstation:3000/api/v1"
harmony_base_url = "http://m1:8282/hubs/harmony-hub/devices/channel-islands-audio-amp/commands"

myzone = "default"
devices = {}
for fn in evdev.list_devices():
    print(fn)
    dev = evdev.InputDevice(fn)
    if dev.name.find('HBGIC') >= 0:
        devices[dev.fd] = dev
print(devices)
while True:
    r, w, x = select.select(devices, [], [])
    for fd in r:
        for event in devices[fd].read():
            url = None
            cmd = None
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
                method = "GET"
                if state == "DOWN":
                    if code == "PLAYPAUSE":
                        url = "%s/zone/%s/control/playpause" % (roon_base_url, myzone)
                    elif code == "STOP":
                        url = "%s/zone/all/control/pause" % roon_base_url
                        #url = "%s/zone/%s/control/stop" % (base_url, myzone)
                    elif code == "REWIND":
                        url = "%s/zone/%s/control/previous" % (roon_base_url, myzone)
                    elif code == "FASTFORWARD":
                        url = "%s/zone/%s/control/next" % (roon_base_url, myzone)
                    elif code == "INFO":
                        method = "POST"
                        url = "%s/mute" % harmony_base_url
                if state == "HOLD" or state == "DOWN":
                    if code == "UP":
                        method = "POST"
                        url = "%s/volume-up" % harmony_base_url
                    elif code == "DOWN":
                        method = "POST"
                        url = "%s/volume-down" % harmony_base_url
            if url:
                print(method, url)
                try:
                    if method == "GET":
                        req = requests.get(url)
                    else:
                        req = requests.post(url)
                except:
                    print("Request to %s failed" % (url))
            if cmd:
                print(" ".join(cmd))
                subprocess.call(cmd)