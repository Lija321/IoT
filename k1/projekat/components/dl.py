from simulators.dl import SimulatedDoorLight


class DoorLightController:
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


def build_door_light(settings):
    if settings.get("simulated", False):
        impl = SimulatedDoorLight()
    else:
        from sensors.dl import DoorLight

        impl = DoorLight(settings["pin"], settings.get("active_high", True))
    return DoorLightController(impl)
