import random
import time


def run_ds_simulator(delay, callback, stop_event):
    pressed = False
    while True:
        if random.random() < 0.3:
            pressed = not pressed
        callback(pressed)
        if stop_event.is_set():
            break
        time.sleep(delay)
