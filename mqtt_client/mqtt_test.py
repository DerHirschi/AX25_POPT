import paho.mqtt.client as mqtt
import json
import time
import logging

# ==================== KONFIGURATION ====================
BROKER = "192.168.1.30"  # oder "homeassistant.local"
PORT = 1883
USERNAME = "popt"  # oder "mqtt-user"
PASSWORD = "1234567890"

DEVICE_ID = "MD2SAW"  # eindeutig für dein Gerät
DEVICE_NAME = "PoPT"  # Name, der in HA angezeigt wird

DISCOVERY_PREFIX = "homeassistant"

# Topics
STATUS_TOPIC = f"popt/status"
AVAILABILITY_TOPIC = f"popt/availability"
CMD_TOPIC = f"popt/cmd/#"  # für Befehle von HA

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION1,      # <--- das ist der wichtige Teil
    client_id=f"PoPT-{DEVICE_ID}"
)


# ==================== CALLBACKS ====================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("✅ Mit MQTT-Broker verbunden")
        client.publish(AVAILABILITY_TOPIC, "online", qos=1, retain=True)

        # Discovery nur einmalig beim Verbinden senden
        send_discovery()

        # Befehle abonnieren
        client.subscribe(CMD_TOPIC)
    else:
        logger.error(f"Verbindungsfehler: {rc}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        logger.info(f"Befehl empfangen → {msg.topic}: {payload}")

        # Hier deine PoPT-Befehlslogik einbauen
        # z.B. if payload.get("action") == "reboot": ...

    except Exception as e:
        logger.warning(f"Ungültiges JSON auf {msg.topic}: {e}")


# ==================== DISCOVERY SENDEN ====================
def send_discovery():
    """Sendet die Discovery-Konfiguration für das Gerät + mehrere Entities"""
    device = {
        "identifiers": [DEVICE_ID],
        "name": DEVICE_NAME,
        "manufacturer": "MD2SAW / P.ython o.ther P.acket T.erminal",
        "model": "PoPT",
        "sw_version": "1.0.0"  # optional
    }

    # --- Beispiel: Sensor "Temperatur" ---
    temp_config = {
        "name": "Temperatur",
        "unique_id": f"{DEVICE_ID}_temperature",
        "device": device,
        "state_topic": STATUS_TOPIC,
        "value_template": "{{ value_json.temperature | float }}",
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "availability_topic": AVAILABILITY_TOPIC,
        "payload_available": "online",
        "payload_not_available": "offline"
    }
    client.publish(f"{DISCOVERY_PREFIX}/sensor/{DEVICE_ID}_temperature/config",
                   json.dumps(temp_config), qos=1, retain=True)

    # --- Beispiel: Sensor "Uptime" ---
    uptime_config = {
        "name": "Uptime",
        "unique_id": f"{DEVICE_ID}_uptime",
        "device": device,
        "state_topic": STATUS_TOPIC,
        "value_template": "{{ value_json.uptime | int }}",
        "unit_of_measurement": "s",
        "icon": "mdi:clock-outline"
    }
    client.publish(f"{DISCOVERY_PREFIX}/sensor/{DEVICE_ID}_uptime/config",
                   json.dumps(uptime_config), qos=1, retain=True)

    # --- Beispiel: Binary Sensor "Online/Status" ---
    binary_config = {
        "name": "PoPT Online",
        "unique_id": f"{DEVICE_ID}_online",
        "device": device,
        "state_topic": AVAILABILITY_TOPIC,
        "payload_on": "online",
        "payload_off": "offline",
        "device_class": "connectivity"
    }
    client.publish(f"{DISCOVERY_PREFIX}/binary_sensor/{DEVICE_ID}_online/config",
                   json.dumps(binary_config), qos=1, retain=True)

    # Weitere Entities (Sensor, Switch, Number, Button etc.) einfach hier hinzufügen

    logger.info("📡 MQTT Discovery Konfiguration gesendet")


# ==================== STATUS PUBLISHEN ====================
def publish_status():
    """Deine aktuellen PoPT-Werte als JSON"""
    status = {
        "temperature": 38.7,
        "uptime": int(time.time() - start_time),
        "status": "running",
        "version": "1.0.0",
        # füge hier alle relevanten Werte hinzu
    }
    client.publish(STATUS_TOPIC, json.dumps(status), qos=1, retain=True)


# ==================== MAIN ====================
if __name__ == "__main__":
    start_time = time.time()

    # Authentifizierung (falls nötig)
    if USERNAME and PASSWORD:
        client.username_pw_set(USERNAME, PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message

    client.will_set(AVAILABILITY_TOPIC, "offline", qos=1, retain=True)  # Last Will

    client.connect(BROKER, PORT, 60)
    client.loop_start()

    try:
        while True:
            publish_status()
            time.sleep(30)  # alle 30 Sekunden aktualisieren
    except KeyboardInterrupt:
        logger.info("Beenden...")
        client.publish(AVAILABILITY_TOPIC, "offline", qos=1, retain=True)
    finally:
        client.disconnect()