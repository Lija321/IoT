import random
import time


def generate_distances(threshold_cm):
    distance = threshold_cm + 5
    while True:
        # Simulate door movement with small random walks
        change = random.uniform(-5, 5)
        distance = max(1, distance + change)
        yield distance


def run_dus_simulator(delay, threshold_cm, callback, stop_event):
    for distance in generate_distances(threshold_cm):
        callback(distance, distance > threshold_cm)
        if stop_event.is_set():
            break
        time.sleep(delay)
