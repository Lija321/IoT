"""
Broker postavke za MQTT – kao na Vezbama (Vezbe7).
HOSTNAME i PORT učitavaju se iz settings.json (mqtt) ili env.
"""
import os

try:
    from settings import load_settings, get_mqtt_config
    _cfg = get_mqtt_config(load_settings())
    HOSTNAME = os.environ.get("MQTT_BROKER", _cfg.get("broker_host", "localhost"))
    PORT = int(os.environ.get("MQTT_PORT", str(_cfg.get("broker_port", 1883))))
except Exception:
    HOSTNAME = os.environ.get("MQTT_BROKER", "localhost")
    PORT = int(os.environ.get("MQTT_PORT", "1883"))
