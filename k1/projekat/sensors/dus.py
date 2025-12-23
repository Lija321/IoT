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

class UltrasonicSensor:
    def __init__(self, trigger_pin, echo_pin):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        GPIO.output(self.trigger_pin, GPIO.LOW)
        time.sleep(0.05)

    def measure_distance_cm(self, timeout=0.02):
        GPIO.output(self.trigger_pin, GPIO.LOW)
        time.sleep(0.0002)
        GPIO.output(self.trigger_pin, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trigger_pin, GPIO.LOW)

        start_time = time.time()
        while GPIO.input(self.echo_pin) == 0:
            if time.time() - start_time > timeout:
                return None
        pulse_start = time.time()

        while GPIO.input(self.echo_pin) == 1:
            if time.time() - pulse_start > timeout:
                return None
        pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        # Speed of sound in air is ~34300 cm/s
        distance = pulse_duration * 17150
        return distance


def run_dus_loop(sensor, delay, threshold_cm, callback, stop_event):
    while True:
        distance = sensor.measure_distance_cm()
        if distance is not None:
            is_open = distance > threshold_cm
            callback(distance, is_open)
        if stop_event.is_set():
            break
        time.sleep(delay)
