import threading
import time

from simulators.dpir import run_pir_simulator


SENSOR_TYPE = "dpir"


def _pir_callback(motion_detected, print_cb, enqueue_reading, device_info,
                  topic_prefix, topic_override, simulated):
    if print_cb:
        print_cb(motion_detected)
    if enqueue_reading is not None and device_info is not None:
        enqueue_reading(
            device_info=device_info,
            sensor_type=SENSOR_TYPE,
            value={"motion": motion_detected},
            simulated=simulated,
            topic_prefix=topic_prefix,
            sensor_topic_override=topic_override,
        )


def run_dpir(settings, threads, stop_event, enqueue_reading=None, device_info=None,
             topic_prefix=None, topic_override=None):
    delay = settings.get("delay", 1)
    simulated = settings.get("simulated", False)
    topic_override = topic_override or settings.get("mqtt_topic")

    def pir_callback(motion_detected):
        _pir_callback(
            motion_detected,
            lambda m: _print_pir(m),
            enqueue_reading, device_info, topic_prefix, topic_override, simulated,
        )

    def _print_pir(motion_detected):
        t = time.localtime()
        print("=" * 20)
        print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
        state = "MOTION" if motion_detected else "NO MOTION"
        print(f"Door PIR: {state}")

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
