import threading
import time

from simulators.dus import run_dus_simulator


def dus_callback(distance_cm, is_open):
    t = time.localtime()
    print("=" * 20)
    print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
    state = "OPEN" if is_open else "CLOSED"
    print(f"Door: {state}")
    print(f"Distance: {distance_cm:.2f} cm")


def run_dus(settings, threads, stop_event):
    delay = settings.get("delay", 1)
    threshold_cm = settings.get("threshold_cm", 10)
    if settings["simulated"]:
        print("Starting dus1 simulator")
        dus_thread = threading.Thread(
            target=run_dus_simulator,
            args=(delay, threshold_cm, dus_callback, stop_event),
        )
        dus_thread.start()
        threads.append(dus_thread)
        print("Dus1 simulator started")
    else:
        from sensors.dus import UltrasonicSensor, run_dus_loop

        print("Starting dus1 loop")
        sensor = UltrasonicSensor(settings["trigger_pin"], settings["echo_pin"])
        dus_thread = threading.Thread(
            target=run_dus_loop,
            args=(sensor, delay, threshold_cm, dus_callback, stop_event),
        )
        dus_thread.start()
        threads.append(dus_thread)
        print("Dus1 loop started")
