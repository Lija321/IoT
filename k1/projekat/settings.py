import json
import os


def load_settings(file_path="settings.json"):
    path = file_path
    if not os.path.isabs(path):
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, file_path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_device_info(settings):
    """Return device info dict for MQTT payloads (pi_id, device_name, optional fields)."""
    dev = settings.get("device", {})
    return {
        "pi_id": dev.get("pi_id", "PI1"),
        "device_name": dev.get("device_name", "unknown"),
        "location": dev.get("location"),
        "room": dev.get("room"),
    }


def get_mqtt_config(settings):
    """Return MQTT broker and topic config."""
    mqtt = settings.get("mqtt", {})
    return {
        "broker_host": mqtt.get("broker_host", "localhost"),
        "broker_port": mqtt.get("broker_port", 1883),
        "topic_prefix": mqtt.get("topic_prefix", "iot/sensors"),
    }


def get_batch_config(settings):
    """Return batch size and flush interval for daemon."""
    batch = settings.get("batch", {})
    return {
        "batch_size": batch.get("batch_size", 10),
        "flush_interval_sec": batch.get("flush_interval_sec", 5),
    }