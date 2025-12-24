import argparse
import threading
import time

from settings import load_settings
from components.dus import run_dus
from components.dpir import run_dpir
from components.dms import run_dms
from components.ds import run_ds
from components.db import build_buzzer
from components.dl import build_door_light

try:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
except:  # pragma: no cover - GPIO not available in simulations
    pass


def run_sensor_mode(settings):
    threads = []
    stop_event = threading.Event()
    try:
        if "DUS1" in settings:
            dus1_settings = settings["DUS1"]
            run_dus(dus1_settings, threads, stop_event)
        if "DPIR1" in settings:
            dpir1_settings = settings["DPIR1"]
            run_dpir(dpir1_settings, threads, stop_event)
        if "DMS1" in settings:
            dms1_settings = settings["DMS1"]
            run_dms(dms1_settings, threads, stop_event)
        if "DS1" in settings:
            ds1_settings = settings["DS1"]
            run_ds(ds1_settings, threads, stop_event)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping sensors")
        for t in threads:
            stop_event.set()


def run_actuator_cli(settings):
    print("Actuator CLI: commands -> on/off/toggle [buzzer|light], status [buzzer|light|all], exit")

    controllers = {}
    if "DB1" in settings:
        controllers["buzzer"] = build_buzzer(settings["DB1"])
    if "DL1" in settings:
        controllers["light"] = build_door_light(settings["DL1"])

    if not controllers:
        print("No actuators configured (missing DB1/DL1 in settings). Exiting actuator CLI.")
        return

    def handle_command(cmd, target=None):
        if cmd == "status":
            if target:
                controller = controllers.get(target)
                if controller:
                    print(f"{target.capitalize()} {controller.status()}")
                else:
                    print(f"Unknown target '{target}'.")
            else:
                for name, controller in controllers.items():
                    print(f"{name.capitalize()} {controller.status()}")
            return

        if target is None:
            if len(controllers) == 1:
                target = next(iter(controllers))
            else:
                print("Specify target: buzzer or light")
                return
        controller = controllers.get(target)
        if not controller:
            print(f"Unknown target '{target}'.")
            return
        if cmd == "on":
            controller.on()
        elif cmd == "off":
            controller.off()
        elif cmd == "toggle":
            controller.toggle()
        else:
            print("Commands: on/off/toggle [target], status [target], exit")
            return
        print(f"{target.capitalize()} {controller.status()}")

    try:
        while True:
            parts = input("> ").strip().lower().split()
            if not parts:
                continue
            cmd = parts[0]
            if cmd in ("exit", "quit"):
                break
            target = parts[1] if len(parts) > 1 else None
            handle_command(cmd, target)
    except KeyboardInterrupt:
        print("\nExiting actuator CLI")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IoT project runner")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("-s", "--sensors", action="store_true", help="Run sensor readers")
    mode_group.add_argument("-a", "--actuators", action="store_true", help="Run actuator CLI")
    args = parser.parse_args()

    settings = load_settings()
    if args.actuators:
        run_actuator_cli(settings)
    else:
        run_sensor_mode(settings)
