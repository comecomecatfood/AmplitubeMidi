#!/usr/bin/python3
# -*- coding: utf-8 -*-`

import time
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import (
    CONTROLLER_CHANGE
)

from gpiozero import Button, LED
from signal import pause

midiout, port_name = open_midioutput(1)

class FootController(object):
    def __init__(self):
        self.power_led = LED(6)

        self.moller = {
            'led': LED(17),
            # value 100 is off
            'value': 100,
            'sig': 0x52,
        }

        self.ts = {
            'led': LED(27),
            # value 100 is off
            'value': 100,
        }

        self.delay = {
            'led': LED(22),
            # value 100 is off
            'value': 100,
        }

        self.bunk = {
            'value': 0,
            '1bit_led': LED(24),
        }

        self.right_button = Button(13)
        self.right_button.when_pressed = self.right_button_push
        self.center_button = Button(19)
        self.center_button.when_pressed = self.center_button_push
        self.left_button = Button(26)
        self.left_button.when_pressed = self.left_button_push

        self.other_button = Button(23)

        self.power_led.on()

    def ts_change(self):
        if self.ts['value'] == 100:
            self.ts['led'].on()
            self.ts['value'] = 0
            print('TS ON')
        else:
            self.ts['led'].off()
            self.ts['value'] = 100
            print('TS OFF')
        controller_change = [CONTROLLER_CHANGE, 0x50, self.ts['value']]
        midiout.send_message(controller_change)

    def delay_change(self):
        if self.delay['value'] == 100:
            self.delay['led'].on()
            self.delay['value'] = 0
            print('Delay ON')
        else:
            self.delay['led'].off()
            self.delay['value'] = 100
            print('Delay OFF')
        controller_change = [CONTROLLER_CHANGE, 0x51, self.delay['value']]
        midiout.send_message(controller_change)

    def moller_change(self):
        if self.moller['value'] == 100:
            self.moller['led'].on()
            self.moller['value'] = 0
            print('Moller ON')
        else:
            self.moller['led'].off()
            self.moller['value'] = 100
            print('Moller OFF')
        controller_change = [CONTROLLER_CHANGE, self.moller['sig'], self.moller['value']]
        midiout.send_message(controller_change)

    def right_button_push(self):
        if self.bunk['value'] == 0:
            self.moller_change()

    def center_button_push(self):
        if self.bunk['value'] == 0:
            self.ts_change()

    def left_button_push(self):
        if self.bunk['value'] == 0:
            self.delay_change()


foot_controller = FootController()

print('Start!')

pause()
