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

		@staticmethod
		def setmode(mode):
			pass

		@staticmethod
		def setup(pin, mode):
			pass

		@staticmethod
		def output(pin, state):
			pass

		@staticmethod
		def input(pin):
			return GPIOStub.LOW

	GPIO = GPIOStub()


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
