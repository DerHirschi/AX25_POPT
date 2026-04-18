from cfg.constant import VER
from fnc.socket_fnc import get_my_hostname

# ====================== BASIS-KONFIG ======================
DISCOVERY_PREFIX        = "homeassistant"
SYS_AVAILABILITY_TOPIC  = f"popt/availability"
SYS_STATUS_TOPIC        = f"popt/status"
SYS_DEVICE_ID           = f"{get_my_hostname()}".replace('.', '-')


# ====================== PoPT CORE DEVICE ======================
def get_popt_core_device():
    return {
        "identifiers": [f"popt_{SYS_DEVICE_ID}"],
        "name": f"PoPT - {SYS_DEVICE_ID}",
        "manufacturer": "MD2SAW / Python other Packet Terminal",
        "model": "PoPT Core",
        "sw_version": VER
    }


# ====================== CORE ENTITIES (PoPT System) ======================
# Hier fügst du einfach neue Sensoren hinzu!
CORE_ENTITIES = {
    "uptime": {
        "component": "sensor",
        "name": "Uptime",
        "unique_id": f"{SYS_DEVICE_ID}_uptime",
        "state_topic": SYS_STATUS_TOPIC,
        "value_template": "{{ value_json.uptime | int }}",
        "unit_of_measurement": "s",
        "icon": "mdi:clock-outline",
    },
    "online": {
        "component": "binary_sensor",
        "name": "PoPT Online",
        "unique_id": f"{SYS_DEVICE_ID}_online",
        "state_topic": SYS_AVAILABILITY_TOPIC,
        "payload_on": "online",
        "payload_off": "offline",
        "device_class": "connectivity",
    },
    # ← NEUEN CORE-SENSOR HIER HINZUFÜGEN (Beispiel):
    # "cpu_temp": {
    #     "component": "sensor",
    #     "name": "CPU Temperatur",
    #     "unique_id": f"{SYS_DEVICE_ID}_cpu_temp",
    #     "state_topic": SYS_STATUS_TOPIC,
    #     "value_template": "{{ value_json.cpu_temp | float }}",
    #     "unit_of_measurement": "°C",
    #     "device_class": "temperature",
    # },
}

# ====================== STATION ENTITIES (Templates) ======================
# Hier definierst du, welche Sensoren eine Station haben kann
STATION_ENTITY_TEMPLATES = {
    "connected": {
        "component": "binary_sensor",
        "name": "{station} Connected",
        "unique_id": "popt_station_{station}_connected",
        "state_topic": "popt/station/{station}/status",
        "value_template": "{{ value_json.connected | lower }}",   # bleibt so
        "payload_on": "true",      # wichtig: als String
        "payload_off": "false",    # wichtig: als String
        "device_class": "connectivity",
        "icon": "mdi:connection",
    },

    # === CMD
    "notify": {
        "component": "notify",                    # wichtig: "notify"
        "name": "{station} PoPT Beacon",
        "unique_id": "popt_station_{station}_notify",
        "command_topic": "popt/station/{station}/notify",   # hier sendet HA die Benachrichtigung hin
        "device_class": "notify",                 # optional
        "icon": "mdi:video-input-antenna",
        # Weitere Optionen möglich (z.B. qos, retain etc.)
    },
    # ← NEUEN STATION-SENSOR HIER HINZUFÜGEN (Beispiel):
    # "signal": {
    #     "component": "sensor",
    #     "name": "{station} Signal",
    #     "unique_id": "popt_station_{station}_signal",
    #     "state_topic": "popt/station/{station}/status",
    #     "value_template": "{{ value_json.signal | int }}",
    #     "unit_of_measurement": "dBm",
    #     "device_class": "signal_strength",
    #     "icon": "mdi:signal",
    # },
}


def get_station_device(station_call: str):
    """Device-Objekt für eine einzelne Station"""
    return {
        "identifiers": [f"popt_station_{station_call.lower()}"],
        "name": f"Station {station_call}",
        "manufacturer": "MD2SAW",
        "model": "PoPT Station",
        "via_device": f"popt_{SYS_DEVICE_ID}",  # schön gruppiert unter PoPT
    }


def build_entity_config(base_config: dict, station_call: str | None = None):
    """Ersetzt Platzhalter {station} und bereitet die Config vor"""
    config = base_config.copy()

    if station_call:
        for key, value in list(config.items()):   # list() um während Iteration zu modifizieren
            if key in ["unique_id", "state_topic", "command_topic"]:
                config[key] = config[key].format(station=station_call.lower())
            elif key  == "name":
                config[key] = value.format(station=station_call)  # .lower() für Sicherheit

    return config

