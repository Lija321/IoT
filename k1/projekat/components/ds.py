import threading
import time

from simulators.ds import run_ds_simulator


SENSOR_TYPE = "ds"


def _ds_callback(pressed, print_cb, enqueue_reading, device_info,
                 topic_prefix, topic_override, simulated):
    if print_cb:
        print_cb(pressed)
    if enqueue_reading is not None and device_info is not None:
        enqueue_reading(
            device_info=device_info,
            sensor_type=SENSOR_TYPE,
            value={"pressed": pressed},
            simulated=simulated,
            topic_prefix=topic_prefix,
            sensor_topic_override=topic_override,
        )


def run_ds(settings, threads, stop_event, enqueue_reading=None, device_info=None,
           topic_prefix=None, topic_override=None):
    delay = settings.get("delay", 0.1)
    simulated = settings.get("simulated", False)
    topic_override = topic_override or settings.get("mqtt_topic")

    def ds_callback(pressed):
        _ds_callback(
            pressed,
            lambda p: _print_ds(p),
            enqueue_reading, device_info, topic_prefix, topic_override, simulated,
        )

    def _print_ds(pressed):
        t = time.localtime()
        print("=" * 20)
        print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
        state = "CLOSED" if pressed else "OPEN"
        print(f"Door Button: {state}")

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
