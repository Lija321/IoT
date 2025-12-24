import random
import time


def run_dms_simulator(delay, keymap, callback, stop_event, allow_multi=True):
    keys = [k for row in keymap for k in row]
    pressed = set()
    while True:
        # Occasionally change the pressed set to mimic key activity
        if random.random() < 0.25:
            if pressed:
                pressed = set()
            else:
                if allow_multi and len(keys) > 1 and random.random() < 0.2:
                    pressed = set(random.sample(keys, 2))
                else:
                    pressed = {random.choice(keys)}
        callback(pressed)
        if stop_event.is_set():
            break
        time.sleep(delay)
