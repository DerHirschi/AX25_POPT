APRS_SW_ID                  = f"APZPOP"  # TODO get SW ID
APRS_TRACER_COMMENT         = "PoPT-Tracer"
APRS_INET_PORT_ID           = 'I-NET'
APRS_CQ_ADDRESSES           = ['ALL', 'QST', 'CQ']
APRS_POS_BEACON_COMMENT_MAX = 40
APRS_IGATE_RATE_LIMIT       = 30 # Max 30 Pakete/Min an IS
APRS_SW_ID_TAP = {
    # Deine Original-Einträge (leicht korrigiert/ergänzt)
    APRS_SW_ID: 'PoPT - Python other Packet Terminal',
    # Häufige weitere Software & Geräte
    'APDW':     'DireWolf (Software Soundcard TNC von WB2OSZ)',  # APDWxx = DireWolf + Version
    'APC':      'APRS/CE (Windows CE / Pocket PC)',  # APCxxx
    'APD':      'Linux aprsd server (älter) / diverse D-Star/Digi-Geräte',  # APDxxx (mehrdeutig)
    'APE':      'PIC-Encoder / Telemetrie-Geräte (z. B. Balloon-Tracker)',  # APExxx

    'APU':      'UI-View32 (sehr verbreitetes Windows-Programm von G4IDE)',
    'APW':      'WinAPRS (von den Sproul-Brüdern)',
    'APX':      'Xastir (Linux/Unix APRS-Client)',
    'APR':      'APRSdos (Original von WB4APR)',
    'APS':      'APRS+SA (von KH2Z)',
    'APO':      'APRSdroid (Android-App)',
    'APDR':     'APRSdroid (genauer Prefix)',
    'APJ':      'YAAC (Yet Another APRS Client) oder jAPRSIgate',
    'APF':      'aprs.fi iOS App (iPhone/iPad)',
    'APK':      'Kenwood TH-D7 / D700 / D710 / D72 etc. (Handfunkgeräte)',
    'APY':      'Yaesu FT1D / FT2D / FT3D / FT5D etc.',
    'API':      'ICOM D-Star Geräte',
    'APT':      'Byonics TinyTrak (Tracker)',
    'APN':      'PacComm TNC / diverse Hardware-TNCs',
    'APZ':      'Experimentelle Software / 6-Zeichen-Gridsquare',

    # Weitere nützliche / moderne Einträge
    'APLO':     'LoRa KISS TNC/Tracker (z. B. SQ9MDD)',
    'APLS':     'SARIMESH (Such- und Rettungs-Mesh)',
    'APATAR':   'ATA-R APRS Digipeater',
    'APDIGI':   'Digipeater ON (z. B. bei Satelliten oder QIKCOM)',
    'APESPG':   'ESP32/ESP8266 SmartBeacon / APRS-IS Client',
    'APESPW':   'ESP Weather Station',

    # Generische / alte
    'APRS':     'Generisches APRS (Fallback)',
    'BEACON':   'Altes Beacon-Format (nicht software-spezifisch)',
}