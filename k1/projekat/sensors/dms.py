import time

import RPi.GPIO as GPIO


class MembraneSwitch:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def read_pressed(self):
        return GPIO.input(self.pin) == GPIO.HIGH


def run_dms_loop(sensor, delay, callback, stop_event):
    last_state = None
    while True:
        pressed = sensor.read_pressed()
        if pressed != last_state:
            callback(pressed)
            last_state = pressed
        if stop_event.is_set():
            break
        time.sleep(delay)
