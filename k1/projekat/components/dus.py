"""
DUS (ultrasonic distance) komponenta – struktura kao na Vezbama (Vezbe3 uds, Vezbe7 component).
Callback šalje payload s measurement, simulated, runs_on, name, value (batch MQTT).
"""
import threading
import time

from simulators.dus import run_dus_simulator


SENSOR_TYPE = "dus"


def _dus_callback(distance_cm, is_open, print_callback, enqueue_reading, device_info,
                  topic_prefix, topic_override, simulated, verbose=True):
    """Kao dht_callback na Vezbama: verbose za ispis, enqueue za batch (measurement, runs_on, name, value)."""
    if verbose and print_callback:
        print_callback(distance_cm, is_open)
    if enqueue_reading is not None and device_info is not None:
        enqueue_reading(
            device_info=device_info,
            sensor_type=SENSOR_TYPE,
            value={"distance_cm": round(distance_cm, 2), "is_open": is_open},
            simulated=simulated,
            topic_prefix=topic_prefix,
            sensor_topic_override=topic_override,
        )


def run_dus(settings, threads, stop_event, enqueue_reading=None, device_info=None,
            topic_prefix=None, topic_override=None):
    """Kao run_dht na Vezbama: simulated -> simulator thread, inače sensor loop; callback za ispis + enqueue."""
    delay = settings.get("delay", 1)
    threshold_cm = settings.get("threshold_cm", 10)
    simulated = settings.get("simulated", False)
    topic_override = topic_override or settings.get("mqtt_topic")

    def dus_callback(distance_cm, is_open):
        _dus_callback(
            distance_cm, is_open,
            lambda d, o: _print_dus(d, o),
            enqueue_reading, device_info, topic_prefix, topic_override, simulated,
            verbose=True,
        )

    def _print_dus(distance_cm, is_open):
        t = time.localtime()
        print("=" * 20)
        print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
        state = "OPEN" if is_open else "CLOSED"
        print(f"Door: {state}")
        print(f"Distance: {distance_cm:.2f} cm")

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
