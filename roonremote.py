#!/usr/bin/env python3
import evdev
import select
import requests

base_url = "http://192.168.1.31:3000/api/v1"
devices = {}
for fn in evdev.list_devices():
    dev = evdev.InputDevice(fn)
    if dev.name.find('HBGIC') >= 0:
        devices[dev.fd] = dev
print(devices)
while True:
    r, w, x = select.select(devices, [], [])
    for fd in r:
        for event in devices[fd].read():
            url = None
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
                        url = "%s/zone/current/control/playpause" % base_url
                    elif code == "STOP":
                        url = "%s/zone/all/control/pause" % base_url
                    elif code == "REWIND":
                        url = "%s/zone/current/control/previous" % base_url
                    elif code == "FASTFORWARD":
                        url = "%s/zone/current/control/next" % base_url
            if url:
                print(url)
                req = requests.put(url)