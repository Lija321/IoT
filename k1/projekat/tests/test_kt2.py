"""
Testovi za KT2: settings, queue/enqueue, komponente (bez GPIO/MQTT brokera).
"""
import queue
import threading
import time

import pytest


def test_settings_load_and_device_info():
    from settings import load_settings, get_device_info, get_mqtt_config, get_batch_config
    s = load_settings()
    assert "device" in s
    assert "mqtt" in s
    assert "batch" in s
    di = get_device_info(s)
    assert "pi_id" in di
    assert "device_name" in di
    mqtt = get_mqtt_config(s)
    assert "broker_host" in mqtt
    assert "topic_prefix" in mqtt
    batch = get_batch_config(s)
    assert "batch_size" in batch
    assert "flush_interval_sec" in batch


def test_mqtt_batch_enqueue():
    from settings import get_device_info, load_settings
    from mqtt_batch import make_enqueue
    s = load_settings()
    di = get_device_info(s)
    q = queue.Queue()
    enq = make_enqueue(q)
    enq(device_info=di, sensor_type="dus", value={"distance_cm": 10.5, "is_open": True},
        simulated=True, topic_prefix="iot/sensors")
    assert q.qsize() == 1
    msg = q.get_nowait()
    assert msg["sensor_type"] == "dus"
    assert msg["measurement"] == "dus"  # format kao na Vezbama
    assert msg["runs_on"] == di.get("pi_id")
    assert msg["name"] == di.get("device_name")
    assert msg["simulated"] is True
    assert msg["value"]["distance_cm"] == 10.5
    assert msg["value"]["is_open"] is True
    assert "device" in msg


def test_actuator_mqtt_topic_prefix():
    from settings import load_settings
    from actuator_mqtt import get_actuator_state_topic_prefix
    s = load_settings()
    prefix = get_actuator_state_topic_prefix(s)
    assert "actuators" in prefix
    assert "state" in prefix


def test_run_dus_callback_enqueues_when_provided():
    """Bez stvarnog threada: provjera da run_dus prihvaća enqueue i device_info."""
    from settings import load_settings, get_device_info, get_mqtt_config
    from components.dus import run_dus
    s = load_settings()
    di = get_device_info(s)
    mqtt_cfg = get_mqtt_config(s)
    topic_prefix = mqtt_cfg.get("topic_prefix", "iot/sensors")
    q = queue.Queue()
    from mqtt_batch import make_enqueue
    enq = make_enqueue(q)
    threads = []
    stop = threading.Event()
    run_dus(
        s["DUS1"], threads, stop,
        enqueue_reading=enq, device_info=di, topic_prefix=topic_prefix,
    )
    assert len(threads) == 1
    time.sleep(2.5)  # nekoliko očitanja simulacije
    stop.set()
    threads[0].join(timeout=2)
    assert q.qsize() >= 1
    msg = q.get_nowait()
    assert msg["sensor_type"] == "dus"
    assert "value" in msg
    assert "distance_cm" in msg["value"] or "is_open" in msg["value"]


def test_server_app_health():
    """Flask app: health endpoint vraća 200 i status ok."""
    from server.app import app
    with app.test_client() as c:
        r = c.get("/health")
        assert r.status_code == 200
        data = r.get_json()
        assert data.get("status") == "ok"


def test_server_actuator_api_validation():
    """API /api/actuator: prazan/invalid payload -> 400 ili 503; valid -> 200 ili 503."""
    from server.app import app
    with app.test_client() as c:
        r = c.post("/api/actuator", json={})
        # 503 ako MQTT nije spojen (provjera prije body-a), 400 ako validacija prva
        assert r.status_code in (400, 503)
        r2 = c.post("/api/actuator", json={"actuator": "buzzer", "command": "invalid"})
        assert r2.status_code in (400, 503)
        r3 = c.post("/api/actuator", json={"actuator": "buzzer", "command": "on"})
        assert r3.status_code in (200, 503)
