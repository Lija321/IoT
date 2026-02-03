# Docker – spoljni servisi za KT2

MQTT broker (Mosquitto), InfluxDB 2, Grafana.

## Pokretanje

```bash
cd docker
cp .env.example .env   # opciono prilagodi
docker compose up -d
```

## Servisi

| Servis    | Port  | Opis |
|----------|-------|------|
| Mosquitto | 1883 | MQTT broker |
| InfluxDB 2 | 8086 | Baza (org=iot, bucket=iot, token iz .env) |
| Grafana   | 3000 | Vizualizacija (admin/admin ili iz .env) |

## Povezivanje aplikacije

- **PI / main.py**: MQTT na `localhost:1883` (ili `host.docker.internal` ako radiš u Dockeru).
- **Server (Flask)**:
  ```bash
  export INFLUX_URL=http://localhost:8086
  export INFLUX_TOKEN=kt2-influxdb-token   # isto kao INFLUX_ADMIN_TOKEN u .env
  export INFLUX_ORG=iot
  export INFLUX_BUCKET=iot
  python -m server.app
  ```
- **Grafana**: http://localhost:3000 (admin/admin). Timezone: **Europe/Belgrade**. Datasource InfluxDB, bucket **iot**. Dashboard se učitava automatski – levi meni **Dashboards** → folder **KT2** → **KT2 IoT senzori i aktuatori**. Ako ga nema, ponovo pokreni Grafana: `docker compose up -d --force-recreate grafana`.

**Simulator radi ali se podaci ne upisuju?** Proveri redom:
1. **Docker radi**: `docker compose ps` – Mosquitto i InfluxDB moraju biti Up.
2. **Server je pokrenut** u posebnom terminalu s tokenom:
   ```bash
   export INFLUX_URL=http://localhost:8086 INFLUX_TOKEN=kt2-influxdb-token INFLUX_ORG=iot INFLUX_BUCKET=iot
   python -m server.app
   ```
   U izlazu treba da vidiš: `[Server] MQTT spojen...` i `InfluxDB token=postavljen`. Ako piše `token=NIJE postavljen`, podaci se ne upisuju.
3. **Senzori šalju na MQTT**: `python main.py -s`. Ako vidiš `[MQTT batch] Broker nije dostupan`, MQTT ne radi – proveri da li je `docker compose up -d` pokrenut.
4. U Grafani stavi vremenski opseg npr. **Last 15 minutes** ili **Last 1 hour**.

## Zaustavljanje

```bash
docker compose down
# Sa volumenima: docker compose down -v
```
