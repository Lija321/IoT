import threading
import time

from simulators.ds import run_ds_simulator


def ds_callback(pressed):
    t = time.localtime()
    print("=" * 20)
    print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
    state = "CLOSED" if pressed else "OPEN"
    print(f"Door Button: {state}")


def run_ds(settings, threads, stop_event):
    delay = settings.get("delay", 0.1)
    if settings["simulated"]:
        print("Starting ds1 simulator")
        ds_thread = threading.Thread(
            target=run_ds_simulator,
            args=(delay, ds_callback, stop_event),
        )
        ds_thread.start()
        threads.append(ds_thread)
        print("Ds1 simulator started")
    else:
        from sensors.ds import DoorButton, run_ds_loop

        print("Starting ds1 loop")
        sensor = DoorButton(settings["pin"])
        ds_thread = threading.Thread(
            target=run_ds_loop,
            args=(sensor, delay, ds_callback, stop_event),
        )
        ds_thread.start()
        threads.append(ds_thread)
        print("Ds1 loop started")
