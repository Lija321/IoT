from simulators.db import SimulatedBuzzer


class BuzzerController:
    def __init__(self, impl):
        self.impl = impl
        self.state = False
        self.off()

    def on(self):
        self.impl.on()
        self.state = True

    def off(self):
        self.impl.off()
        self.state = False

    def toggle(self):
        if self.state:
            self.off()
        else:
            self.on()

    def status(self):
        return "ON" if self.state else "OFF"


def build_buzzer(settings):
    if settings.get("simulated", False):
        impl = SimulatedBuzzer()
    else:
        from sensors.db import Buzzer

        impl = Buzzer(settings["pin"])
    return BuzzerController(impl)
