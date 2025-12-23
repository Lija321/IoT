import threading
import time

from simulators.dms import run_dms_simulator


def dms_callback(pressed):
    t = time.localtime()
    print("=" * 20)
    print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
    state = "CLOSED" if pressed else "OPEN"
    print(f"Door Switch: {state}")


def run_dms(settings, threads, stop_event):
    delay = settings.get("delay", 0.2)
    if settings["simulated"]:
        print("Starting dms1 simulator")
        dms_thread = threading.Thread(
            target=run_dms_simulator,
            args=(delay, dms_callback, stop_event),
        )
        dms_thread.start()
        threads.append(dms_thread)
        print("Dms1 simulator started")
    else:
        from sensors.dms import MembraneSwitch, run_dms_loop

        print("Starting dms1 loop")
        sensor = MembraneSwitch(settings["pin"])
        dms_thread = threading.Thread(
            target=run_dms_loop,
            args=(sensor, delay, dms_callback, stop_event),
        )
        dms_thread.start()
        threads.append(dms_thread)
        print("Dms1 loop started")
