# Kontrolna tačka 2 (KT2)

Proširenje skripte za PI1: konfiguracija uređaja, slanje mjerenja MQTT-om u batch-evima putem daemon niti, server (Flask) koji prima MQTT i upisuje u InfluxDB, vizualizacija u Grafani.

---

## Kako pokrenuti sve

Treba ti **3 terminala** (ili 2 + browser). Redosled je bitan.

### Korak 1: Docker (MQTT, InfluxDB, Grafana)

```bash
cd docker
cp .env.example .env   # samo prvi put
docker compose up -d
```

Proveri: `docker compose ps` – sva tri kontejnera (mosquitto, influxdb, grafana) treba da budu Up.

### Korak 2: Server (prima MQTT, upisuje u InfluxDB)

U **drugom terminalu**:

```bash
cd /putanja/do/projekat   # root projekta (gde je main.py)

export INFLUX_URL=http://localhost:8086
export INFLUX_TOKEN=kt2-influxdb-token
export INFLUX_ORG=iot
export INFLUX_BUCKET=iot

python -m server.app
```

Ostavi da radi. Treba da vidiš: `[Server] MQTT spojen...` i `InfluxDB token=postavljen`.

### Korak 3: Senzori (simulator šalje podatke na MQTT)

U **trećem terminalu**:

```bash
cd /putanja/do/projekat

pip install -r requirements.txt   # samo prvi put
python main.py -s
```

Ostavi da radi. Ne bi trebalo da se pojavi `[MQTT batch] Broker nije dostupan`.

### Korak 4: Grafana (vizualizacija)

U browseru otvori **http://localhost:3000** → login **admin** / **admin** → **Dashboards** → **KT2 IoT senzori i aktuatori**. Vremenski opseg gore desno: npr. **Last 15 minutes** ili **Last 1 hour**.

---

**Aktuatori (opciono):** u nekom terminalu `python main.py -a` – CLI za buzzer/svjetlo i MQTT komande.

**Zaustavljanje:** u svakom terminalu gde radi server ili senzori pritisni **Ctrl+C**. Docker: `cd docker && docker compose down`.

**Brzi start:** iz root-a projekta pokreni `./scripts/run-all.sh` – podiže Docker i ispisuje tačne komande za terminal 2 i 3 (server i senzori).

---

## Zahtjevi

- **Python 3.8+**
- **MQTT broker** (npr. Mosquitto) na `localhost:1883` ili adresa iz `settings.json` / env
- **InfluxDB 2.x** (za server i Grafana)
- **Grafana** (za panele)

## Konfiguracija

### settings.json

- **device**: `pi_id`, `device_name`, opciono `location`, `room`
- **mqtt**: `broker_host`, `broker_port`, `topic_prefix` (npr. `iot/pi1/sensors`)
- **batch**: `batch_size`, `flush_interval_sec` za daemon nit koja šalje batch-eve

Po senzoru može se navesti `mqtt_topic` (npr. u `DUS1`) da se topic overriduje za taj senzor.

### Pokretanje na PI (senzori + batch MQTT)

```bash
# instalacija
pip install -r requirements.txt

# senzorski mod: čita senzore, stavlja očitanja u red, daemon nit šalje batch-eve MQTT-om
python main.py -s
```

Izmjerene/simulirane vrijednosti šalju se u batch-evima putem **jedne generičke daemon niti**. Svaka poruka sadrži tag `simulated` (true/false). Nema deadlocka; kritična sekcija je minimalna (samo `queue.put` u nitima senzora i `queue.get` u daemon niti).

### Pokretanje na PI (aktuatori + MQTT stanje i komande)

```bash
python main.py -a
```

Aktuatori: CLI kao u KT1. Stanje se šalje na MQTT nakon svake komande (on/off/toggle). PI pretplaćen na topic komandi može primati naredbe s servera (Grafana / API).

### Server (Flask + MQTT subscriber + InfluxDB)

Server prima poruke s MQTT brokera i upisuje ih u InfluxDB 2.x.

```bash
# env (ili .env)
export INFLUX_URL=http://localhost:8086
export INFLUX_TOKEN=your-admin-token
export INFLUX_ORG=iot
export INFLUX_BUCKET=iot

# pokretanje (iz root direktorija projekta)
python -m server.app
# ili: python server/app.py
```

- **MQTT**: pretplata na `iot/+/sensors/#` i `iot/+/actuators/#` (stanja, ne komande)
- **InfluxDB**: jedan bucket (npr. `iot`); measurement = tip senzora (`dus`, `dpir`, `dms`, `ds`) ili `actuator`; tagovi: `simulated`, `pi_id`, `device_name`; polja iz payloada `value`

API za slanje komandi aktuatorima (PI mora biti pokrenut s `-a` i pretplaćen na topic komandi):

```bash
curl -X POST http://localhost:5000/api/actuator \
  -H "Content-Type: application/json" \
  -d '{"actuator": "buzzer", "command": "on", "pi_id": "PI1"}'
```

### Grafana

1. Dodaj **InfluxDB** datasource (Flux, InfluxDB 2.x), npr. URL `http://localhost:8086`, token i org.
2. Uvezi dashboard: **grafana/dashboard-kt2.json** (Import → Upload JSON).
3. Na dashboardu odaberi datasource i bucket (npr. `iot`).

Svaki tip senzora ima svoj panel:

- **DUS** – udaljenost (cm) i stanje vrata (otvoreno/zatvoreno)
- **DPIR** – PIR pokret
- **DMS** – pritisnute tipke (keypad)
- **DS** – dugme vrata (pritisnuto/otvoreno)
- **Aktuatori** – stanje (buzzer/svjetlo)

Aktivacija aktuatora: preko API-ja `POST /api/actuator` (npr. iz Grafana HTTP Request ili eksternog alata).

## Struktura

- **main.py** – `-s` senzori + red + daemon nit, `-a` aktuatori + MQTT stanje/komande
- **mqtt_batch.py** – generička daemon nit, batch slanje MQTT-om, `make_enqueue()`
- **actuator_mqtt.py** – pretplata na komande, slanje stanja na MQTT
- **components/dus.py, dpir.py, dms.py, ds.py** – enqueue očitanja (sensor_type, value, simulated, device_info, topic)
- **server/app.py** – Flask, MQTT subscriber, upis u InfluxDB
- **server/influx.py** – mapiranje MQTT payload → InfluxDB Point (senzori + actuator)
- **server/config.py** – MQTT i InfluxDB iz env
- **grafana/dashboard-kt2.json** – dashboard s panelima po tipu senzora i aktuatora

## Deadlock i mutexi

- Koristi se samo **queue.Queue** za red očitanja; nema dodatnih mutexa.
- Senzorske niti samo pozivaju `queue.put()`.
- Daemon nit radi `queue.get(timeout=...)`, sastavlja batch i šalje MQTT (I/O van bilo kakvog locka).
- Aktuator MQTT: jedna nit za MQTT loop; komande iz poruke pozivaju `controller.on/off/toggle`; nema dijeljenih lockova s CLI-jem.
