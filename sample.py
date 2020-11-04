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
        self.green_led = LED(17)
        self.blue_led = LED(27)
        self.yellow_led = LED(22)
        self.red_led = LED(24)
        self.white_led = LED(25)

        self.moller = {
            'led': self.green_led,
            # value 100 is off
            'value': 100,
            'sig': 0x52,
        }

        self.ts = {
            'led': self.blue_led,
            # value 100 is off
            'value': 100,
            'sig': 0x50,
        }

        self.delay = {
            'led': self.yellow_led,
            # value 100 is off
            'value': 100,
            'sig': 0x51,
        }

        self.mute = {
            # value 100 is off
            'value': 100,
            'sig': 0x54,
        }

        self.bunk = {
            'value': 0,
        }

        self.amp = {
            'value': 'jcm900',
            'jcm900': {
                'led': self.red_led,
                'sig': 0x00
            },
            'twin reverb': {
                'led': self.white_led,
                'sig': 0x01
            }
        }
        self.amp['jcm900']['led'].on()

        self.right_button = Button(13)
        self.right_button.when_pressed = self.right_button_push
        self.center_button = Button(19)
        self.center_button.when_pressed = self.center_button_push
        self.left_button = Button(26)
        self.left_button.when_pressed = self.left_button_push

        self.other_button = Button(23)
        self.other_button.when_pressed = self.mute_change

        self.power_led.on()

    def ts_change(self, on_off=''):
        if on_off == '' and self.ts['value'] == 100:
            self.ts['led'].on()
            self.ts['value'] = 0
            print('TS ON')
        elif on_off == '' and self.ts['value'] == 0:
            self.ts['led'].off()
            self.ts['value'] = 100
            print('TS OFF')
        elif on_off == 'on':
            self.ts['led'].on()
            self.ts['value'] = 0
            print('TS ON')
        else:
            self.ts['led'].off()
            self.ts['value'] = 100
            print('TS OFF')
        controller_change = [CONTROLLER_CHANGE, self.ts['sig'], self.ts['value']]
        midiout.send_message(controller_change)

    def delay_change(self, on_off=''):
        if on_off == '' and self.delay['value'] == 100:
            self.delay['led'].on()
            self.delay['value'] = 0
            print('Delay ON')
        elif on_off == '' and self.delay['value'] == 0:
            self.delay['led'].off()
            self.delay['value'] = 100
            print('Delay OFF')
        elif on_off == 'on':
            self.delay['led'].on()
            self.delay['value'] = 0
            print('Delay ON')
        else:
            self.delay['led'].off()
            self.delay['value'] = 100
            print('Delay OFF')
        controller_change = [CONTROLLER_CHANGE, self.delay['sig'], self.delay['value']]
        midiout.send_message(controller_change)

    def moller_change(self, on_off=''):
        if on_off != 'off' and self.moller['value'] == 100:
            self.moller['led'].on()
            self.moller['value'] = 0
            print('Moller ON')
        else:
            self.moller['led'].off()
            self.moller['value'] = 100
            print('Moller OFF')
        controller_change = [CONTROLLER_CHANGE, self.moller['sig'], self.moller['value']]
        midiout.send_message(controller_change)

    def mute_change(self):
        if self.mute['value'] == 100:
            self.mute['value'] = 0
            self.red_led.blink()
            self.moller_change('off')
            self.ts_change('off')
            self.delay_change('off')
            print('Mute ON')
            self.bunk_status()
        else:
            self.mute['value'] = 100
            print('Mute OFF')
            if self.bunk['value'] in [0, 1]:
                self.moller_change('off')
                self.ts_change('off')
                self.delay_change('off')
                # jcm900 ON
                self.red_led.on()
                if self.amp['value'] != 'jcm900':
                    self.amp['value'] = 'jcm900'
                    controller_change = [CONTROLLER_CHANGE, self.amp['jcm900']['sig'], 100]
                    midiout.send_message(controller_change)

        controller_change = [CONTROLLER_CHANGE, self.mute['sig'], self.mute['value']]
        midiout.send_message(controller_change)

    def right_button_push(self):
        if self.mute['value'] == 0:
            return
        if self.bunk['value'] == 0:
            self.moller_change()
        elif self.bunk['value'] == 1:
            self.ts_change('off')
            self.delay_change('off')

    def center_button_push(self):
        if self.mute['value'] == 0:
            self.decrement_bunk()
            return
        if self.bunk['value'] == 0:
            self.ts_change()
        elif self.bunk['value'] == 1:
            self.ts_change('on')
            self.delay_change('off')

    def left_button_push(self):
        if self.mute['value'] == 0:
            self.increment_bunk()
            return
        if self.bunk['value'] == 0:
            self.delay_change()
        elif self.bunk['value'] == 1:
            self.ts_change('on')
            self.delay_change('on')

    def increment_bunk(self):
        if self.bunk['value'] == 7:
            self.bunk['value'] = 0
        else:
            self.bunk['value'] += 1
        print('Bunk Change: Number {}'.format(self.bunk['value']))
        self.bunk_status()

    def decrement_bunk(self):
        if self.bunk['value'] == 0:
            self.bunk['value'] = 7
        else:
            self.bunk['value'] -= 1
        print('Bunk Change: Number {}'.format(self.bunk['value']))
        self.bunk_status()


    def bunk_status(self):
        if self.bunk['value'] == 0:
            self.green_led.off()
            self.blue_led.off()
            self.yellow_led.off()
        elif self.bunk['value'] == 1:
            self.green_led.on()
            self.blue_led.off()
            self.yellow_led.off()
        elif self.bunk['value'] == 2:
            self.green_led.off()
            self.blue_led.on()
            self.yellow_led.off()
        elif self.bunk['value'] == 3:
            self.green_led.on()
            self.blue_led.on()
            self.yellow_led.off()
        elif self.bunk['value'] == 4:
            self.green_led.off()
            self.blue_led.off()
            self.yellow_led.on()
        elif self.bunk['value'] == 5:
            self.green_led.on()
            self.blue_led.off()
            self.yellow_led.on()
        elif self.bunk['value'] == 6:
            self.green_led.off()
            self.blue_led.on()
            self.yellow_led.on()
        elif self.bunk['value'] == 7:
            self.green_led.on()
            self.blue_led.on()
            self.yellow_led.on()


foot_controller = FootController()

print('Start!')

pause()
