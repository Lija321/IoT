import threading
import time

from simulators.dms import run_dms_simulator


DEFAULT_KEYMAP = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"],
]


def dms_callback(pressed_keys):
    t = time.localtime()
    print("=" * 20)
    print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
    if pressed_keys:
        print(f"Keys pressed: {', '.join(sorted(pressed_keys))}")
    else:
        print("Keys pressed: none")


def run_dms(settings, threads, stop_event):
    delay = settings.get("delay", 0.2)
    keymap = settings.get("keymap", DEFAULT_KEYMAP)
    row_pins = settings.get("row_pins", settings.get("rows", [25, 8, 7, 1]))
    col_pins = settings.get("col_pins", settings.get("cols", [12, 16, 20, 21]))
    allow_multi = settings.get("allow_multi", True)

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
