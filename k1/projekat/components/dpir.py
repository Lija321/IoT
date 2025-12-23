import threading
import time

from simulators.dpir import run_pir_simulator


def pir_callback(motion_detected):
    t = time.localtime()
    print("=" * 20)
    print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
    state = "MOTION" if motion_detected else "NO MOTION"
    print(f"Door PIR: {state}")


def run_dpir(settings, threads, stop_event):
    delay = settings.get("delay", 1)
    if settings["simulated"]:
        print("Starting dpir1 simulator")
        pir_thread = threading.Thread(
            target=run_pir_simulator,
            args=(delay, pir_callback, stop_event),
        )
        pir_thread.start()
        threads.append(pir_thread)
        print("Dpir1 simulator started")
    else:
        from sensors.dpir import PIRSensor, run_pir_loop

        print("Starting dpir1 loop")
        sensor = PIRSensor(settings["pin"])
        pir_thread = threading.Thread(
            target=run_pir_loop,
            args=(sensor, delay, pir_callback, stop_event),
        )
        pir_thread.start()
        threads.append(pir_thread)
        print("Dpir1 loop started")
