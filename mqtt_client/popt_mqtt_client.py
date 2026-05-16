
from cfg.logger_config import logger

try:
    import paho.mqtt.client as mqtt
    PAHO = True
except ImportError:
    mqtt = None
    PAHO = False


class PoptMqttDefault:
    def __init__(self):
        self.import_error       = True
        self.mqtt_conn_end      = True
        self._mqtt_is_running   = False
        self._mqtt_conf         = {}

    @staticmethod
    def mqtt_client_task():
        return False

    def register_station(self, station_call: str):
        pass

    def publish_station_status(self, station_call: str, status_tab: dict):
        pass


if not PAHO:
    logger.info("PoPT-MQTT: Python-Packet paho-mqtt not installed !!")
    logger.info("PoPT-MQTT: If u want to use PoPT-MQTT-Client Feature,")
    logger.info("PoPT-MQTT: u have to install paho-mqtt.")
    logger.info("PoPT-MQTT: pip install paho-mqtt")
    PoPT_MQTT = PoptMqttDefault()
else:
    logger.info("PoPT-MQTT: Setting up PoPT-MQTT Client")
    import time
    from classes.CLbuffers import ListBuffer
    import json
    from mqtt_client.mqtt_devices import (
        get_popt_core_device,
        CORE_ENTITIES,
        STATION_ENTITY_TEMPLATES,
        build_entity_config,
        get_station_device,
        SYS_DEVICE_ID,
        DISCOVERY_PREFIX,
        SYS_AVAILABILITY_TOPIC,
        SYS_STATUS_TOPIC
    )


    # Topics
    CMD_TOPIC = f"popt/cmd/#"  # für Befehle von HA

    # ======
    mqtt_conf = dict(
        BROKER_addr="192.168.1.30",
        BROKER_port=1883,
        BROKER_user="popt",
        BROKER_pass="1234567890",
    )


    class PoptMQTT(PoptMqttDefault):
        def __init__(self, mqtt_cfg: dict):
            super().__init__()
            self.import_error       = False
            self.mqtt_conn_end      = False
            self._mqtt_is_running   = False
            self._mqtt_conf         = mqtt_conf
            if not all((
                    self._mqtt_conf.get('BROKER_addr', None),
                    self._mqtt_conf.get('BROKER_port', None),
                    self._mqtt_conf.get('BROKER_user', None),
                    self._mqtt_conf.get('BROKER_pass', None),
            )):
                logger.error("PoPT-MQTT: MQTT Config Error. Check Broker Address/Username/Password ")
                raise AttributeError("Check MQTT Config !!")

            # ****************************************************
            # self._mqtt_device = MQTT_DEVICE
            self._mqtt_conn = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION1,
                client_id=f"PoPT-{SYS_DEVICE_ID}"
            )
            self._mqtt_conn.username_pw_set(self._mqtt_conf.get('BROKER_user', ''),
                                            self._mqtt_conf.get('BROKER_pass', ''))

            # ** CALLBACKS
            self._mqtt_conn.on_connect = self._on_connect
            self._mqtt_conn.on_message = self._on_message
            # ********************

            self._mqtt_conn.will_set(SYS_AVAILABILITY_TOPIC, "offline", qos=1, retain=True)  # Last Will

            self._mqtt_conn.connect(self._mqtt_conf.get('BROKER_addr', ''),
                                    self._mqtt_conf.get('BROKER_port', ''),
                                    60)
            # ********************
            self._active_stations = set()  # wird später automatisch befüllt
            # ********************
            self._publisher_tasker_q = ListBuffer()
            # ********************
            self._mqtt_is_running = True

            self._mqtt_conn.loop_start()

        # ==================== CALLBACKS ====================
        def _on_connect(self, client, userdata, flags, rc):
            if rc == 0:
                logger.info("PoPT-MQTT: ✅ Connected to MQTT-Broker")
                client.publish(SYS_AVAILABILITY_TOPIC, "online", qos=1, retain=True)
                # Discovery nur einmalig beim Verbinden senden
                self._send_all_discovery()
                # Befehle abonnieren
                client.subscribe(CMD_TOPIC)
            else:
                logger.error(f"PoPT-MQTT: Verbindungsfehler: {rc}")

        def _on_message(self, client, userdata, msg):
            try:
                topic = msg.topic
                # === Notify Befehl von HA ===
                if topic.endswith("/notify"):
                    self._handle_notify(topic, msg.payload)
                    return
                payload = json.loads(msg.payload.decode('utf-8'))
                logger.info(f"PoPT-MQTT: Befehl empfangen → {topic} | {payload}")
                # Hier kannst du später weitere Befehle hinzufügen
            except Exception as e:
                print(msg.payload)
                logger.warning(f"PoPT-MQTT: Ungültiges JSON auf {msg.topic}: {e}")
                logger.debug(f"PoPT-MQTT: payload: {msg.payload}")

        def _handle_notify(self, topic: str, payload: bytearray):
            """Verarbeitet Benachrichtigungen von HA"""

            message = payload.decode('UTF-8', 'ignore')
            station = topic.replace('/notify', '').split('/')[-1]
            if not message:
                logger.warning("PoPT-Notify: Keine Nachricht im Payload")
                return

            logger.info(f"PoPT-Notify erhalten an: {station}, Text: {message}")


            # Beispiel: Einfache Konsolenausgabe (ersetze durch deine echte Anzeige)
            print(
                f"\n=== PoPT NOTIFICATION ===\nNachricht: {message}\n========================\n")


        # ==================== DISCOVERY (alles zentral) ====================
        def _send_all_discovery(self):
            """Sendet Core + alle bekannten Stationen"""
            # 1. PoPT Core Device + Entities
            core_device = get_popt_core_device()
            for key, base in CORE_ENTITIES.items():
                config = build_entity_config(base)
                config["device"] = core_device

                # Availability nur bei normalen Sensoren
                if key != "online":
                    config["availability_topic"] = SYS_AVAILABILITY_TOPIC
                    config["payload_available"] = "online"
                    config["payload_not_available"] = "offline"

                topic = f"{DISCOVERY_PREFIX}/{config['component']}/{config['unique_id']}/config"
                self._mqtt_conn.publish(topic, json.dumps(config), qos=1, retain=True)
                logger.info(f"Discovery → Core: {config['name']}")

            # 2. Alle Stationen
            for station in self._active_stations:
                self._send_station_discovery(station)

            logger.info("PoPT-MQTT: 📡 Alle Discovery-Konfigurationen gesendet")

        def _send_station_discovery(self, station_call: str):
            station_device = get_station_device(station_call)
            for key, base in STATION_ENTITY_TEMPLATES.items():
                config = build_entity_config(base, station_call)
                config["device"] = station_device

                topic = f"{DISCOVERY_PREFIX}/{config['component']}/{config['unique_id']}/config"
                self._mqtt_conn.publish(topic, json.dumps(config), qos=1, retain=True)
                logger.info(f"Discovery → Station {station_call}: {config['name']}")

        # ==================== PUBLISH METHODS ====================
        def _publish_core_status(self, **data):
            """z.B. uptime, cpu_temp, ..."""
            payload = {"uptime": int(time.time()), **data}
            self._mqtt_conn.publish(SYS_STATUS_TOPIC, json.dumps(payload), qos=1, retain=True)

        def register_station(self, station_call: str):
            """Neue Station aktivieren (einmalig)"""
            if station_call not in self._active_stations:
                self._active_stations.add(station_call)
                self._send_station_discovery(station_call)  # sofort Discovery

                # Automatisch Notify-Topic abonnieren
                notify_topic = f"popt/station/{station_call.lower()}/notify"
                self._mqtt_conn.subscribe(notify_topic)
                logger.info(f"PoPT-MQTT: Notify-Channel abonniert für {station_call}: {notify_topic}")
            """Neue Station aktivieren (einmalig)"""
            if station_call not in self._active_stations:
                self._active_stations.add(station_call)
                self._send_station_discovery(station_call)  # sofort Discovery

                # Automatisch Notify-Topic abonnieren
                notify_topic = f"popt/station/{station_call.lower()}/notify"
                self._mqtt_conn.subscribe(notify_topic)
                logger.info(f"PoPT-MQTT: Notify-Channel abonniert für {station_call}: {notify_topic}")

        def publish_station_status(self, station_call: str, status_tab: dict):
            """Zustand + beliebige Werte einer Station – mit Retain"""
            """
            payload = {
                "connected": connected,          # True/False → wird zu true/false im JSON
                #"last_seen": int(time.time()),
                **extra
            }
            """
            topic = f"popt/station/{station_call.lower()}/status"
            self._publisher_tasker_q.buffer_write(
                (topic, status_tab)
            )
            """Zustand + beliebige Werte einer Station – mit Retain"""
            """
            payload = {
                "connected": connected,          # True/False → wird zu true/false im JSON
                #"last_seen": int(time.time()),
                **extra
            }
            """
            topic = f"popt/station/{station_call.lower()}/status"
            self._publisher_tasker_q.buffer_write(
                (topic, status_tab)
            )

        # ==================== Tasker ====================

        def mqtt_client_task(self):
            if self._mqtt_is_running:
                try:
                    self._publish_core_status()
                    self._publish_station_status_task()
                except Exception as ex:
                    logger.error(ex)
                    self._mqtt_is_running = False

            elif not self.mqtt_conn_end:
                try:
                    self._mqtt_conn.publish(SYS_AVAILABILITY_TOPIC, "offline", qos=1, retain=True)
                except Exception as ex:
                    logger.error(ex)
                finally:
                    self._mqtt_conn.disconnect()
                    self.mqtt_conn_end = True

        def _publish_station_status_task(self):
            n = 10
            while not self._publisher_tasker_q.is_empty and n:
                topic, payload = self._publisher_tasker_q.buffer_read
                self._mqtt_conn.publish(topic, json.dumps(payload), qos=1, retain=True)  # ← retain=True ist wichtig!
                n -= 1


    PoPT_MQTT = PoptMQTT(mqtt_conf)


if __name__ == '__main__':
    mqtt_client = PoPT_MQTT
    if not mqtt_client.import_error:
        mqtt_client.mqtt_client_task()
        time.sleep(5)
        PoPT_MQTT.register_station("MD4SAW")
        #PoPT_MQTT.register_station("MD1TES")
        tr = False
        while True:
            try:
                mqtt_client.publish_station_status('MD4SAW', {
                    "connected": tr,  # True/False → wird zu true/false im JSON
                    #"last_seen": int(time.time()),
                })

                mqtt_client.mqtt_client_task()
                time.sleep(15)
                tr = not tr
            except KeyboardInterrupt:
                print("Beende Verbindung zu MQTT-Broker")
                break

        mqtt_client._mqtt_is_running = False
        while not mqtt_client.mqtt_conn_end:
            mqtt_client.mqtt_client_task()
            time.sleep(10)

        print("Ende")

