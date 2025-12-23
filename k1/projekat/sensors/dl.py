import RPi.GPIO as GPIO


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
