import time


try:
    import RPi.GPIO as GPIO
except ImportError:
    class GPIOStub:
        BCM = None
        OUT = None
        IN = None
        LOW = 0
        HIGH = 1
        PUD_DOWN = None

        @staticmethod
        def setmode(mode):
            pass

        @staticmethod
        def setup(pin, mode, pull_up_down=None):
            pass

        @staticmethod
        def output(pin, state):
            pass

        @staticmethod
        def input(pin):
            return GPIOStub.LOW

    GPIO = GPIOStub()


class MembraneKeypad:
    def __init__(self, row_pins, col_pins, keymap, allow_multi=True):
        self.row_pins = row_pins
        self.col_pins = col_pins
        self.keymap = keymap
        self.allow_multi = allow_multi

        for row_pin in self.row_pins:
            GPIO.setup(row_pin, GPIO.OUT)
            GPIO.output(row_pin, GPIO.LOW)
        for col_pin in self.col_pins:
            GPIO.setup(col_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def scan_keys(self):
        pressed = []
        for r_idx, row_pin in enumerate(self.row_pins):
            GPIO.output(row_pin, GPIO.HIGH)
            for c_idx, col_pin in enumerate(self.col_pins):
                if GPIO.input(col_pin) == GPIO.HIGH:
                    pressed.append(self.keymap[r_idx][c_idx])
            GPIO.output(row_pin, GPIO.LOW)
        if not self.allow_multi and pressed:
            return {pressed[0]}
        return set(pressed)


def run_dms_loop(keypad, delay, callback, stop_event):
    last_pressed = None
    while True:
        pressed = keypad.scan_keys()
        if pressed != last_pressed:
            callback(pressed)
            last_pressed = pressed
        if stop_event.is_set():
            break
        time.sleep(delay)
