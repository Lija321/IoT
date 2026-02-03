"""
KT2: Actuator MQTT on PI: publish state when it changes, subscribe to commands.
Single thread for MQTT loop; no mutex needed (controller calls from main thread).
"""
import json
import threading
import time

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

TOPIC_COMMAND = "iot/{pi_id}/actuators/command"
TOPIC_STATE = "iot/{pi_id}/actuators/state"


def publish_state(client, device_info, topic_prefix, actuator, state):
    if client is None:
        return
    topic = f"{topic_prefix}/{actuator}"
    payload = json.dumps({
        "actuator": actuator,
        "state": state,
        "timestamp": time.time(),
        "device": {k: v for k, v in (device_info or {}).items() if v is not None},
    })
    try:
        client.publish(topic, payload, qos=0)
    except Exception:
        pass


def get_actuator_state_topic_prefix(settings):
    mqtt_cfg = settings.get("mqtt", {})
    prefix = mqtt_cfg.get("topic_prefix", "iot/sensors")
    return prefix.replace("/sensors", "") + "/actuators/state"


def run_actuator_mqtt_listener(settings, controllers, stop_event, client_holder):
    """
    Subscribe to actuator commands and call controller.on/off/toggle.
    Run in a daemon thread. client_holder = [None] to receive the client.
    """
    if mqtt is None or not controllers:
        return
    device_info = settings.get("device", {})
    pi_id = device_info.get("pi_id", "PI1")
    mqtt_cfg = settings.get("mqtt", {})
    broker_host = mqtt_cfg.get("broker_host", "localhost")
    broker_port = mqtt_cfg.get("broker_port", 1883)
    topic_prefix_state = get_actuator_state_topic_prefix(settings)
    topic_command = TOPIC_COMMAND.format(pi_id=pi_id)

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            client.subscribe(topic_command)

    def on_message(client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode("utf-8"))
            actuator = (data.get("actuator") or "").lower()
            command = (data.get("command") or "").lower()
        except Exception:
            return
        ctrl = controllers.get(actuator)
        if ctrl is None or command not in ("on", "off", "toggle"):
            return
        if command == "on":
            ctrl.on()
        elif command == "off":
            ctrl.off()
        else:
            ctrl.toggle()
        publish_state(client, device_info, topic_prefix_state, actuator, ctrl.status())

    client = mqtt.Client(client_id="pi_actuators", clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message
    connected = False
    try:
        client.connect(broker_host, broker_port, keepalive=60)
        client.loop_start()
        client_holder[0] = client
        connected = True
    except Exception:
        pass
    while not stop_event.is_set():
        time.sleep(0.5)
    if client_holder[0] is client:
        client_holder[0] = None
    if connected:
        client.loop_stop()
        client.disconnect()


def start_actuator_mqtt(settings, controllers):
    """
    Start daemon thread that subscribes to actuator commands.
    Returns (thread, stop_event, client_holder). client_holder[0] is set to MQTT client
    when connected; use it to call publish_state from main thread.
    """
    if mqtt is None or not controllers:
        return None, None, [None]
    stop_event = threading.Event()
    client_holder = [None]
    thread = threading.Thread(
        target=run_actuator_mqtt_listener,
        args=(settings, controllers, stop_event, client_holder),
        name="actuator_mqtt",
        daemon=True,
    )
    thread.start()
    return thread, stop_event, client_holder
