"""
KT2: Generic daemon thread that batches sensor readings from a queue and
publishes them via MQTT. No custom mutexes; queue.Queue is thread-safe.
Critical section is minimal: only queue.get() / put(); publish runs outside.
"""
import json
import queue
import threading
import time

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None


def _create_client(broker_host, broker_port):
    if mqtt is None:
        return None
    client = mqtt.Client(client_id="pi_sensors", clean_session=True)
    try:
        client.connect(broker_host, broker_port, keepalive=60)
        client.loop_start()
    except Exception:
        return None
    return client


def _publish_batch(client, topic_prefix, messages):
    """Publish list of reading dicts. Payload format kao na Vezbama: measurement, simulated, runs_on, name, value."""
    if client is None or not messages:
        return
    for msg in messages:
        topic = msg.get("topic") or f"{topic_prefix}/{msg.get('sensor_type', msg.get('measurement', 'unknown'))}"
        # Format kao na Vezbama (Vezbe7): measurement, simulated, runs_on, name, value
        payload = json.dumps({
            "measurement": msg.get("measurement", msg.get("sensor_type")),
            "sensor_type": msg.get("sensor_type"),
            "simulated": msg.get("simulated", False),
            "runs_on": msg.get("runs_on", ""),
            "name": msg.get("name", ""),
            "timestamp": msg.get("timestamp"),
            "device": msg.get("device", {}),
            "value": msg.get("value"),
        }, default=str)
        try:
            client.publish(topic, payload, qos=0)
        except Exception:
            pass


def _run_daemon(reading_queue, stop_event, broker_host, broker_port, topic_prefix,
                batch_size, flush_interval_sec):
    """
    Single daemon thread: drain queue in batches, publish via MQTT.
    Uses queue.get(timeout=...) to flush periodically; no deadlock (no nested locks).
    """
    client = _create_client(broker_host, broker_port)
    if client is None:
        print("[MQTT batch] Broker nije dostupan – proveri da Docker radi i da je MQTT na {}:{}. Podaci se ne šalju.".format(broker_host, broker_port), flush=True)
    batch = []
    deadline = time.monotonic() + flush_interval_sec
    while not stop_event.is_set():
        timeout = max(0.01, deadline - time.monotonic())
        try:
            item = reading_queue.get(timeout=timeout)
        except queue.Empty:
            item = None
        if item is not None:
            batch.append(item)
        if len(batch) >= batch_size or (time.monotonic() >= deadline and batch):
            _publish_batch(client, topic_prefix, batch)
            batch = []
            deadline = time.monotonic() + flush_interval_sec
    if batch and client:
        _publish_batch(client, topic_prefix, batch)
    if client:
        client.loop_stop()
        client.disconnect()


def start_batch_daemon(settings, reading_queue, stop_event):
    """
    Start one generic daemon thread for all sensors. Returns the thread.
    Broker adresa iz settings ili broker_settings (kao na Vezbama).
    """
    try:
        from broker_settings import HOSTNAME, PORT
        broker_host, broker_port = HOSTNAME, PORT
    except ImportError:
        broker_host = broker_port = None
    mqtt_cfg = settings.get("mqtt", {})
    batch_cfg = settings.get("batch", {})
    if broker_host is None:
        broker_host = mqtt_cfg.get("broker_host", "localhost")
    if broker_port is None:
        broker_port = mqtt_cfg.get("broker_port", 1883)
    topic_prefix = mqtt_cfg.get("topic_prefix", "iot/sensors")
    batch_size = batch_cfg.get("batch_size", 10)
    flush_interval_sec = batch_cfg.get("flush_interval_sec", 5)
    daemon = threading.Thread(
        target=_run_daemon,
        args=(reading_queue, stop_event, broker_host, broker_port, topic_prefix,
              batch_size, flush_interval_sec),
        name="mqtt_batch_daemon",
        daemon=True,
    )
    daemon.start()
    return daemon


def make_enqueue(reading_queue):
    """Return a callable that enqueues one reading. Only queue.put(); minimal critical section."""

    def enqueue_reading(device_info, sensor_type, value, simulated,
                        topic_prefix=None, sensor_topic_override=None):
        """
        value: dict or scalar. Payload uključuje measurement, runs_on, name kao na Vezbama.
        """
        import time as _time
        device = {k: v for k, v in (device_info or {}).items() if v is not None}
        msg = {
            "measurement": sensor_type,
            "sensor_type": sensor_type,
            "simulated": bool(simulated),
            "runs_on": (device_info or {}).get("pi_id", ""),
            "name": (device_info or {}).get("device_name", ""),
            "timestamp": _time.time(),
            "device": device,
            "value": value,
        }
        if sensor_topic_override:
            msg["topic"] = sensor_topic_override
        elif topic_prefix:
            msg["topic"] = f"{topic_prefix}/{sensor_type}"
        reading_queue.put(msg)

    return enqueue_reading
