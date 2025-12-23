
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


class DoorLight:
    def __init__(self, pin, active_high=True):
        self.pin = pin
        self.active_high = active_high
        GPIO.setup(self.pin, GPIO.OUT)
        self.off()

    def on(self):
        GPIO.output(self.pin, GPIO.HIGH if self.active_high else GPIO.LOW)

    def off(self):
        GPIO.output(self.pin, GPIO.LOW if self.active_high else GPIO.HIGH)
