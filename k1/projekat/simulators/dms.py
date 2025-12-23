import random
import time


def run_dms_simulator(delay, callback, stop_event):
    pressed = False
    while True:
        # Randomly toggle pressed state to mimic door open/close
        if random.random() < 0.3:
            pressed = not pressed
        callback(pressed)
        if stop_event.is_set():
            break
        time.sleep(delay)
