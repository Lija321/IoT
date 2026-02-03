"""Write sensor and actuator records to InfluxDB (InfluxDB 2.x line protocol)."""
import time

try:
    from influxdb_client import InfluxDBClient, Point
    from influxdb_client.client.write_api import SYNCHRONOUS
except ImportError:
    InfluxDBClient = None
    Point = None
    SYNCHRONOUS = None


def _client(config):
    if InfluxDBClient is None or not config.get("INFLUX_TOKEN"):
        return None
    return InfluxDBClient(
        url=config["INFLUX_URL"],
        token=config["INFLUX_TOKEN"],
        org=config["INFLUX_ORG"],
    )


def write_sensor_reading(client, bucket, org, payload):
    """
    Parse MQTT payload. Format kao na Vezbama: measurement, simulated, runs_on, name, value.
    Point(measurement).tag(simulated, runs_on, name).field(...).
    """
    if client is None or Point is None:
        return
    try:
        measurement = payload.get("measurement") or payload.get("sensor_type") or "unknown"
        simulated = payload.get("simulated", False)
        runs_on = payload.get("runs_on") or (payload.get("device") or {}).get("pi_id", "")
        name = payload.get("name") or (payload.get("device") or {}).get("device_name", "")
        ts = payload.get("timestamp")
        value = payload.get("value")
        if value is None:
            return
        point = (
            Point(measurement)
            .tag("simulated", str(simulated).lower())
            .tag("runs_on", str(runs_on))
            .tag("name", str(name))
            .tag("pi_id", str((payload.get("device") or {}).get("pi_id", "")))
            .tag("device_name", str((payload.get("device") or {}).get("device_name", "")))
        )
        if ts is not None:
            point.time(int(ts * 1e9))
        if isinstance(value, dict):
            for k, v in value.items():
                if v is None:
                    continue
                if isinstance(v, bool):
                    point.field(k, v)
                elif isinstance(v, (int, float)):
                    point.field(k, float(v))
                elif isinstance(v, (list, tuple)):
                    point.field(k, ",".join(str(x) for x in v))
                else:
                    point.field(k, str(v))
        else:
            point.field("value", value)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket=bucket, org=org, record=point)
    except Exception as e:
        print("[InfluxDB] Greška pri upisu senzora: {}".format(e), flush=True)


def write_actuator_state(client, bucket, org, payload):
    """Write actuator state change to InfluxDB (measurement=actuator)."""
    if client is None or Point is None:
        return
    try:
        actuator = payload.get("actuator") or "unknown"
        state = str(payload.get("state", "")).lower()
        ts = payload.get("timestamp", time.time())
        device = payload.get("device") or {}
        state_num = 1.0 if state == "on" else 0.0
        point = (
            Point("actuator")
            .tag("actuator", actuator)
            .tag("pi_id", str(device.get("pi_id", "")))
            .tag("device_name", str(device.get("device_name", "")))
            .field("state", state)
            .field("state_num", state_num)
            .time(int(ts * 1e9))
        )
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket=bucket, org=org, record=point)
    except Exception:
        pass
