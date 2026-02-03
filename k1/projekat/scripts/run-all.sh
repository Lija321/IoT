#!/bin/bash
# Pokreće Docker (MQTT, InfluxDB, Grafana), zatim ispisuje komande za server i senzore.
# Koristi: ./scripts/run-all.sh   (iz root-a projekta)

set -e
cd "$(dirname "$0")/.."
PROJECT_ROOT="$PWD"

echo "=== 1. Docker (MQTT, InfluxDB, Grafana) ==="
cd docker
docker compose up -d
cd "$PROJECT_ROOT"
echo ""

echo "=== 2. Otvori DRUGI terminal i pokreni server: ==="
echo "cd $PROJECT_ROOT"
echo "export INFLUX_URL=http://localhost:8086 INFLUX_TOKEN=kt2-influxdb-token INFLUX_ORG=iot INFLUX_BUCKET=iot"
echo "python -m server.app"
echo ""

echo "=== 3. Otvori TREĆI terminal i pokreni senzore: ==="
echo "cd $PROJECT_ROOT"
echo "python main.py -s"
echo ""

echo "=== 4. Grafana: http://localhost:3000 (admin/admin), dashboard KT2 IoT senzori i aktuatori ==="
