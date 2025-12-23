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

class PIRSensor:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN)

    def read_motion(self):
        return GPIO.input(self.pin) == GPIO.HIGH


def run_pir_loop(sensor, delay, callback, stop_event):
    while True:
        motion = sensor.read_motion()
        callback(motion)
        if stop_event.is_set():
            break
        time.sleep(delay)
