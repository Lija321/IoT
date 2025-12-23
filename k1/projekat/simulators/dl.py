class SimulatedDoorLight:
    def __init__(self):
        self.state = False

    def on(self):
        self.state = True
        print("[SIM] Door light ON")

    def off(self):
        self.state = False
        print("[SIM] Door light OFF")
