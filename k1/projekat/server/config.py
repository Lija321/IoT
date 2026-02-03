"""Server config: MQTT broker, InfluxDB URL/token/bucket. Env vars override defaults."""
import os

MQTT_BROKER = os.environ.get("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_TOPIC_SENSORS = os.environ.get("MQTT_TOPIC_SENSORS", "iot/+/sensors/#")
MQTT_TOPIC_ACTUATORS = os.environ.get("MQTT_TOPIC_ACTUATORS", "iot/+/actuators/#")

INFLUX_URL = os.environ.get("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.environ.get("INFLUX_TOKEN", "")
INFLUX_ORG = os.environ.get("INFLUX_ORG", "iot")
INFLUX_BUCKET = os.environ.get("INFLUX_BUCKET", "iot")

SERVER_PORT = int(os.environ.get("PORT", os.environ.get("FLASK_PORT", "5000")))
