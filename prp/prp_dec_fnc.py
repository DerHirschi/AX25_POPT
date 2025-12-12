import datetime

from prp.prp_const import PRP_FLAG, PRP_CTL_TAB


def pack_6bit_int_and_bool(value: int, flag1: bool = False, flag2: bool = False):
    """
    by Grok-AI
    Packt einen 6-Bit-Integer (0–63) und zwei boolesche Flags in ein einzelnes Byte.

    Bit-Aufbau:
        Bit 7       → flag2
        Bit 6       → flag1
        Bit 5–0     → value (6 Bit)

    Beispiel:
        value=45, flag1=True, flag2=False  → 0b00101101 → 45 + 64 = 109 → b'm'
    """
    if not (0 <= value <= 63):
        raise ValueError("6-Bit-Wert muss zwischen 0 und 63 liegen")

    byte_value = (
            (value & 0b00111111) |  # Bits 0–5: Wert
            ((1 if flag1 else 0) << 6) |  # Bit 6: flag1
            ((1 if flag2 else 0) << 7)  # Bit 7: flag2
    )

    return bytes([byte_value])


def unpack_6bit_int_and_bool(data):
    """
    by Grok-AI
    Entpackt ein Byte, das mit pack_6bit_int_and_bool() gepackt wurde.

    Rückgabe: (value: int, flag1: bool, flag2: bool)
    """
    if len(data) < 1:
        raise ValueError("Mindestens ein Byte erforderlich")

    byte  = data[0]
    value = byte & 0b00111111  # Bits 0–5
    flag1 = bool(byte & 0b01000000)  # Bit 6 → 64
    flag2 = bool(byte & 0b10000000)  # Bit 7 → 128

    return value, flag1, flag2


def pack_time_hms(datetime_now):
    """
    by Grok-AI
    Packt aktuelle Uhrzeit (HH:MM:SS) in 3 Bytes BCD – super platzsparend und 100% verlustfrei
    """
    now = datetime_now
    hh = now.hour
    mm = now.minute
    ss = now.second

    # BCD: jedes Nibble = eine Dezimalstelle (0–9)
    return bytes([
        (hh // 10 << 4) | (hh % 10),  # Stunde  00–23 → 0x00–0x23
        (mm // 10 << 4) | (mm % 10),  # Minute  00–59 → 0x00–0x59
        (ss // 10 << 4) | (ss % 10),  # Sekunde 00–59 → 0x00–0x59
    ])


def unpack_time_hms_to_datetime(data: bytes):
    """
    by Grok-AI
    Wandelt die 3 BCD-Bytes wieder in ein echtes datetime-Objekt um
    (Datum = heute, also perfekt für Anzeige im Log oder GUI)
    """
    if len(data) < 3:
        raise ValueError("Brauche 3 Bytes für HH:MM:SS")

    hh = ((data[0] >> 4) & 0x0F) * 10 + (data[0] & 0x0F)
    mm = ((data[1] >> 4) & 0x0F) * 10 + (data[1] & 0x0F)
    ss = ((data[2] >> 4) & 0x0F) * 10 + (data[2] & 0x0F)

    # Heutiges Datum + empfangene Uhrzeit
    return datetime.datetime.now().replace(hour=hh, minute=mm, second=ss, microsecond=0)


# --------------------------------------------------------------
# PRP-METADATEN-DECODER (nur Header, keine Payload-Dekodierung!)
# --------------------------------------------------------------
# Rückgabe: dict mit:
#   'prp_frames'    → Anzahl enthaltener PRP-Frames (bei Batch)
#   'opt_id'        → 0–63 (Port-ID oder Steuerbefehl)
#   'opt_typ'       → Typ Steuerbefehle
#   'tx'            → True = gesendet, False = empfangen
#   'compressed'    → True wenn F2=1 (LZHUF)
#   'payload_len'   → Länge des (escaped) Payloads
#   'is_batch'      → True wenn OPT-ID == 63
#   'raw_len'       → Gesamtlänge des PRP-Pakets
# --------------------------------------------------------------

def decode_prp_metadata(raw_ax25_payload: bytes):
    """
    Vorlage by Grok AI
    Schneller, PRP-Header-Parser für Monitor – nur Metadaten, keine Dekompression, kein Unescaping.
    Gibt None zurück, wenn kein gültiges PRP-Paket erkannt wurde.
    """
    # TODO bessere PRP-Paket validierung.
    #  PRP-Frames mit unbekannter OPT und unplausibler len werden als PRP dekodiert.
    payload_len = len(raw_ax25_payload)
    # Min: FLAG(2) + OPT(1) + LEN(2)
    if payload_len < 5:
        return None, raw_ax25_payload
    # PRP Flag in Payload ?
    if not PRP_FLAG in raw_ax25_payload:
        return None, raw_ax25_payload

    i          = 0
    prp_frames = []
    rest_data  = bytearray()
    while i < payload_len:
        # Flag in rest payload ? > Return
        if not PRP_FLAG in raw_ax25_payload[i:]:
            rest_data += raw_ax25_payload[i:]
            return prp_frames, rest_data
        # < 5 Bytes, Paket kann nicht ausgewertet werden. > Return
        if payload_len - i < 5:
            rest_data += raw_ax25_payload[i:]
            return prp_frames, rest_data
        # PRP-Flag bei i:i +2 ? > weiter
        if raw_ax25_payload[i:i + 2] != PRP_FLAG:
            rest_data += raw_ax25_payload[i].to_bytes(1)
            i         += 1
            continue
        # Versuche Header zu dekodieren
        try:
            # Header
            opt_byte  = int(raw_ax25_payload[2]).to_bytes(1)
            prp_len   = int.from_bytes(raw_ax25_payload[3:5], 'little')
            total_len = 5 + prp_len + 2  # Header(5) + Payload + CRC(2)
            # Opt
            opt_id, tx_flag, compressed = unpack_6bit_int_and_bool(opt_byte)
            opt_typ = PRP_CTL_TAB.get(opt_id, '')
            port_id = opt_id if opt_id < 20 else None
            # Validiere ob Opt Typ existiert
            if port_id is None and not opt_typ:
                rest_data += raw_ax25_payload[i].to_bytes(1)
                i += 1
                continue
            # PRP Batch Packet ?
            is_batch = (opt_id == 63)

            prp_frames.append({
                'is_prp'        : True,
                'opt_id'        : opt_id,
                'opt_typ'       : opt_typ,
                'port_id'       : port_id,
                'tx'            : tx_flag,
                'compressed'    : compressed,
                'payload_len'   : prp_len,
                'total_len'     : total_len,
                'is_batch'      : is_batch,
                'ctl_type'      : 'PRP-Batch' if is_batch else
                                  ('PRP-Mon' if opt_id < 20 else 'PRP-Cmd'),
            })
            i = i + total_len

        except Exception as ex:
            null       = ex   # Make my IDE happy :-)
            rest_data += raw_ax25_payload[i].to_bytes(1)
            i         += 1
            continue

    return prp_frames, rest_data
