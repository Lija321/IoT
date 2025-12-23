import random
import time


def run_pir_simulator(delay, callback, stop_event):
    motion = False
    while True:
        # Flip motion status occasionally to mimic movement
        if random.random() < 0.3:
            motion = not motion
        callback(motion)
        if stop_event.is_set():
            break
        time.sleep(delay)
