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
        self.ts ={
            'led': LED(17),
            # value 100 is off
            'value': 100,
        }
        self.ts_button = Button(2)
        self.ts_button.when_pressed = self.ts_change

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

foot_controller = FootController()

print('Start!')

pause()
