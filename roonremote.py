#!/usr/bin/env python3
import evdev
import select
import requests
import subprocess


base_url = "http://roonstation:3000/api/v1"
myzone = "Hifi"
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
                if state == "DOWN":
                    if code == "PLAYPAUSE":
                        url = "%s/zone/%s/control/playpause" % (base_url, myzone)
                    elif code == "STOP":
                        url = "%s/zone/all/control/pause" % base_url
                        #url = "%s/zone/%s/control/stop" % (base_url, myzone)
                    elif code == "REWIND":
                        url = "%s/zone/%s/control/previous" % (base_url, myzone)
                    elif code == "FASTFORWARD":
                        url = "%s/zone/%s/control/next" % (base_url, myzone)
                    elif code == "INFO":
                        cmd = ['/root/harmonyHubCLI/bin/harmonyhub-cli', '-l', 'HarmonyHub', '-d', 'Channel Islands Audio Amp', '-c', 'Mute']
                if state == "HOLD" or state == "DOWN":
                    if code == "UP":
                        cmd = ['/root/harmonyHubCLI/bin/harmonyhub-cli', '-l', 'HarmonyHub', '-a', 'Roon', '-c', 'Volume,Volume Up']
                    elif code == "DOWN":
                        cmd = ['/root/harmonyHubCLI/bin/harmonyhub-cli', '-l', 'HarmonyHub', '-a', 'Roon', '-c', 'Volume,Volume Down']
            if url:
                print(url)
                try:
                    req = requests.get(url)
                except:
                    print("Request to %s failed" % (url))
            if cmd:
                print(" ".join(cmd))
                subprocess.call(cmd)