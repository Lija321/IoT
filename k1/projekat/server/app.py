"""
KT2: Flask server that subscribes to MQTT broker and writes sensor/actuator
messages to InfluxDB. Provides optional REST API for actuator commands.
"""
import json
import os
import sys
import threading

# Add project root for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

from server.config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_TOPIC_SENSORS,
    MQTT_TOPIC_ACTUATORS,
    INFLUX_URL,
    INFLUX_TOKEN,
    INFLUX_ORG,
    INFLUX_BUCKET,
    SERVER_PORT,
)
from server.influx import write_sensor_reading, write_actuator_state, _client

app = Flask(__name__)

CONFIG = {
    "INFLUX_URL": INFLUX_URL,
    "INFLUX_TOKEN": INFLUX_TOKEN,
    "INFLUX_ORG": INFLUX_ORG,
    "INFLUX_BUCKET": INFLUX_BUCKET,
}

_influx_client = None
_mqtt_client = None
_influx_warned = False


def get_influx_client():
    global _influx_client
    if _influx_client is None and INFLUX_TOKEN:
        _influx_client = _client(CONFIG)
    return _influx_client


def on_mqtt_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(MQTT_TOPIC_SENSORS)
        client.subscribe(MQTT_TOPIC_ACTUATORS)
        print("[Server] MQTT spojen, pretplata na senzore i aktuatore.", flush=True)
    else:
        print(f"[Server] MQTT konekcija neuspešna, rc={rc}", flush=True)


def on_mqtt_message(client, userdata, msg):
    global _influx_warned
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except Exception:
        return
    influx = get_influx_client()
    if not influx:
        if not _influx_warned:
            _influx_warned = True
            print("[Server] InfluxDB nije podešen (postavi INFLUX_TOKEN), podaci se ne upisuju.", flush=True)
        return
    topic = msg.topic
    if "actuators" in topic and "command" not in topic:
        write_actuator_state(influx, INFLUX_BUCKET, INFLUX_ORG, payload)
    elif "sensors" in topic:
        write_sensor_reading(influx, INFLUX_BUCKET, INFLUX_ORG, payload)


def start_mqtt_listener():
    global _mqtt_client
    if mqtt is None:
        print("[Server] paho-mqtt nije instaliran.", flush=True)
        return
    _mqtt_client = mqtt.Client(client_id="kt2_server", clean_session=True)
    _mqtt_client.on_connect = on_mqtt_connect
    _mqtt_client.on_message = on_mqtt_message
    try:
        _mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        _mqtt_client.loop_start()
        print(f"[Server] MQTT konekcija na {MQTT_BROKER}:{MQTT_PORT}. InfluxDB token={'postavljen' if INFLUX_TOKEN else 'NIJE postavljen'}.", flush=True)
    except Exception as e:
        print(f"[Server] MQTT konekcija neuspešna: {e}", flush=True)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/actuator", methods=["POST"])
def actuator_command():
    """Send actuator command via MQTT (PI subscribes and executes)."""
    if _mqtt_client is None or not _mqtt_client.is_connected():
        return jsonify({"error": "MQTT not connected"}), 503
    data = request.get_json() or {}
    actuator = data.get("actuator")  # buzzer | light
    command = data.get("command")   # on | off | toggle
    device_id = data.get("pi_id", "PI1")
    if not actuator or command not in ("on", "off", "toggle"):
        return jsonify({"error": "actuator and command (on|off|toggle) required"}), 400
    topic = f"iot/{device_id}/actuators/command"
    payload = json.dumps({"actuator": actuator, "command": command})
    _mqtt_client.publish(topic, payload, qos=0)
    return jsonify({"ok": True, "topic": topic})


if __name__ == "__main__":
    start_mqtt_listener()
    app.run(host="0.0.0.0", port=SERVER_PORT, debug=False, use_reloader=False)
