import threading
import time

from simulators.dms import run_dms_simulator


DEFAULT_KEYMAP = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"],
]


SENSOR_TYPE = "dms"


def _dms_callback(pressed_keys, print_cb, enqueue_reading, device_info,
                  topic_prefix, topic_override, simulated):
    if print_cb:
        print_cb(pressed_keys)
    if enqueue_reading is not None and device_info is not None:
        keys_list = list(pressed_keys) if pressed_keys else []
        enqueue_reading(
            device_info=device_info,
            sensor_type=SENSOR_TYPE,
            value={"keys": keys_list, "keys_count": len(keys_list)},
            simulated=simulated,
            topic_prefix=topic_prefix,
            sensor_topic_override=topic_override,
        )


def run_dms(settings, threads, stop_event, enqueue_reading=None, device_info=None,
            topic_prefix=None, topic_override=None):
    delay = settings.get("delay", 0.2)
    keymap = settings.get("keymap", DEFAULT_KEYMAP)
    row_pins = settings.get("row_pins", settings.get("rows", [25, 8, 7, 1]))
    col_pins = settings.get("col_pins", settings.get("cols", [12, 16, 20, 21]))
    allow_multi = settings.get("allow_multi", True)
    simulated = settings.get("simulated", False)
    topic_override = topic_override or settings.get("mqtt_topic")

    def dms_callback(pressed_keys):
        _dms_callback(
            pressed_keys,
            lambda k: _print_dms(k),
            enqueue_reading, device_info, topic_prefix, topic_override, simulated,
        )

    def _print_dms(pressed_keys):
        t = time.localtime()
        print("=" * 20)
        print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
        if pressed_keys:
            print(f"Keys pressed: {', '.join(sorted(pressed_keys))}")
        else:
            print("Keys pressed: none")

    if settings["simulated"]:
        print("Starting keypad simulator")
        dms_thread = threading.Thread(
            target=run_dms_simulator,
            args=(delay, keymap, dms_callback, stop_event, allow_multi),
        )
        dms_thread.start()
        threads.append(dms_thread)
        print("Keypad simulator started")
    else:
        from sensors.dms import MembraneKeypad, run_dms_loop

        print("Starting keypad loop")
        keypad = MembraneKeypad(row_pins, col_pins, keymap, allow_multi=allow_multi)
        dms_thread = threading.Thread(
            target=run_dms_loop,
            args=(keypad, delay, dms_callback, stop_event),
        )
        dms_thread.start()
        threads.append(dms_thread)
        print("Keypad loop started")
