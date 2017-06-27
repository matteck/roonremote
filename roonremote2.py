#!/usr/bin/env python3
import evdev
import select
import requests
import sys

base_url = "http://localhost:3001/roonAPI"
zone_name = "GreenSpeakers"

zones = requests.get("%s/listZones" % base_url).json()['zones']
for z in zones.keys():
    if zones[z]['display_name'] == zone_name:
        zone_id = z
        print(zones[z])
        output_id = zones[z]['outputs'][0]['output_id']
        break
assert(zone_id)
print(zone_id)
print(output_id)
sys.exit()
    
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
                if code =="UP" or code == "DOWN":
                    if state == "HOLD" or state == "DOWN":
                        if code == "DOWN":
                            step = "-1"
                        else:
                            step = "1"
                        r = requests.get("%s/change_volume_step?outputId=%s&step=%s" % (base_url, output_id, step))
                elif state == "DOWN":
                    if code == "PLAYPAUSE":
                        command = "pause" 
                    elif code == "STOP":
                        command = "stop"
                    elif code == "REWIND":
                        command = "previous"
                    elif code == "FASTFORWARD":
                        command = "next"
                    r = requests.get("%s/%s?zoneId=%s" % (base_url, command, zone_id))
                # except:
                #     print("Request to %s failed" % (url))