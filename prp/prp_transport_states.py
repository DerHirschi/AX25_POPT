from enum import Enum
from cfg.logger_config import logger
"""
              DATA ok
   ┌───────────────┐
   │               ▼
ESTABLISHED ────→ ACK_WAIT
   │  ▲              │
   │  │              │ ack_delay abgelaufen
   │  │              ▼
   │  └────────── STOP_ACK_WAIT
   │
   │ Out-of-order / Missing
   ▼
RECOVERY
   │
   │ Alle Lücken geschlossen
   ▼
ESTABLISHED


| Aktueller State | Event              | Neuer State | Aktion            |
| --------------- | ------------------ | ----------- | ----------------- |
| ESTABLISHED     | DATA_OK            | ACK_WAIT    | ack_pending=True  |
| ESTABLISHED     | DATA_OOO           | ACK_WAIT    | nack_pending=True |
| ACK_WAIT        | TIMER_ACK          | ESTABLISHED | send ACK/NACK     |
| ACK_WAIT        | DATA_MORE          | ACK_WAIT    | merge Bitmask     |
| ESTABLISHED     | NACK_RX            | RECOVERY    | nack_active=True  |
| RECOVERY        | RETRY_SENT         | RECOVERY    | retry pending     |
| RECOVERY        | ACK_RX(no missing) | ESTABLISHED | nack_active=False |
| ANY             | RST                | INIT        | reset             |


"""
class PRPState(Enum):
    CLOSED      = "CLOSED"      # Initial / nach RST/FIN
    INIT        = "INIT"        # Warte auf erstes Paket
    SYN_SENT    = "SYN_SENT"    #
    SYN_RCVD    = "SYN_RCVD"    #
    ESTABLISHED = "ESTABLISHED" # Normale Datenübertragung
    ACK_WAIT    = "ACK_WAIT"    # warte bis ACK gesendet werden darf
    RECOVERY    = "RECOVERY"
    FIN_WAIT    = "FIN_WAIT"    # FIN gesendet, warte auf ACK
    CLOSING     = "CLOSING"     # Beide Seiten FIN gesendet
    # Später erweiterbar: SYN_SENT, SYN_RCVD, etc.

# =============================================================================
# Zustandstabelle: (current_state, event) → (new_state, actions)
# =============================================================================
# Event-Typen:
#   "DATA"          – Eingehendes DATA-Paket (SEQ prüfen separat)
#   "ACK"           – Reines ACK (kein Bitmask)
#   "NACK"          – NACK mit Bitmask
#   "SYN"           – Eingehendes SYN
#   "FIN"           – Eingehendes FIN
#   "RST"           – Eingehendes RST
#   "ERROR"         – Eingehendes ERROR
#   "RNR"           – Receive Not Ready (Pausiere Übertragung, z.B. bei belegtem Band)
#   "TIMER_RETRY"   – Retry-Timer abgelaufen
#   "TIMER_KEEP"    – Keepalive-Timer
#   "NO_EVENT"      – tasker() Aufruf ohne neues Paket
#
# Actions: Liste von Funktionsnamen (als String), die aufgerufen werden
# =============================================================================

STATE_TABLE = {
    # -------------------------------------------------
    # INIT
    # -------------------------------------------------
    PRPState.INIT: {
        "DATA":         (PRPState.ESTABLISHED, ["_handle_first_data"]),  # Erstes DATA → direkt ESTABLISHED
        "SYN":          (PRPState.SYN_RCVD, []),
        "SYN_SENT":     (PRPState.SYN_SENT, []),  # Interner Event nach senden
        "SYN_ACK":      (PRPState.ESTABLISHED, []),  # Empfange SYN als ACK
        "RST":          (PRPState.CLOSED, ["_reset_state"]),
        "NO_EVENT":     (PRPState.INIT, []),
    },

    # -------------------------------------------------
    # SYN_SENT
    # -------------------------------------------------
    PRPState.SYN_SENT: {
        "SYN":      (PRPState.ESTABLISHED, []),
        "SYN_ACK":  (PRPState.ESTABLISHED, []),  # Empfange SYN als ACK
        "DATA":     (PRPState.ESTABLISHED, ["_handle_first_data"]),
        "TIMER_RETRY": (PRPState.SYN_SENT, ["_retry_syn"]),  # Neu: Retry SYN
        "NO_EVENT": (PRPState.SYN_SENT, []),
    },

    # -------------------------------------------------
    # SYN_RCVD
    # -------------------------------------------------
    PRPState.SYN_RCVD: {
        "SYN":      (PRPState.ESTABLISHED, []),
        "SYN_ACK":  (PRPState.ESTABLISHED, []),  # Empfange SYN als ACK
        "DATA":     (PRPState.ESTABLISHED, ["_handle_first_data"]),
        "NO_EVENT": (PRPState.ESTABLISHED, []),
    },

    # -------------------------------------------------
    # ESTABLISHED
    # -------------------------------------------------
    PRPState.ESTABLISHED: {
        "START_ACK_WAIT":   (PRPState.ACK_WAIT,    ['_reset_ack_delay']),
        "ACK":              (PRPState.ESTABLISHED, []),
        "NACK":             (PRPState.ESTABLISHED, []),
        "DATA":             (PRPState.ESTABLISHED, []),

        "ENTER_RECOVERY":   (PRPState.RECOVERY,     []),

        "FIN":              (PRPState.FIN_WAIT,     []),
        "RST":              (PRPState.CLOSED,       ["_reset_state"]),
        "TIMER_RETRY":      (PRPState.ESTABLISHED,  ["_retry_pending"]),
        "NO_EVENT":         (PRPState.ESTABLISHED,  []),
    },

    # -------------------------------------------------
    # ACK_WAIT
    # -------------------------------------------------
    PRPState.ACK_WAIT: {
        "STOP_ACK_WAIT":    (PRPState.ESTABLISHED,  ['_reset_ack_delay']),
        "START_ACK_WAIT":   (PRPState.ACK_WAIT,     []),

        "ACK":              (PRPState.ACK_WAIT,     []),
        "NACK":             (PRPState.ACK_WAIT,     []),
        "DATA":             (PRPState.ACK_WAIT,     []),

        "TIMER_RETRY":      (PRPState.ACK_WAIT,     ['_send_delayed_ack_nack']),

        "ENTER_RECOVERY":   (PRPState.RECOVERY,     []),

        "RST":              (PRPState.CLOSED,       ["_reset_state"]),
        "NO_EVENT":         (PRPState.ACK_WAIT,     []),
    },

    # -------------------------------------------------
    # RECOVERY  (NACK aktiv)
    # -------------------------------------------------
    PRPState.RECOVERY: {
        "ENTER_RECOVERY":   (PRPState.RECOVERY,     []),  # idempotent
        "EXIT_RECOVERY":    (PRPState.ESTABLISHED,  []),

        "ACK":              (PRPState.RECOVERY,     []),
        "NACK":             (PRPState.RECOVERY,     []),
        #"START_ACK_WAIT":   (PRPState.ACK_WAIT,     []),

        "TIMER_RETRY":      (PRPState.RECOVERY,     ["_retry_pending"]),

        "RST":              (PRPState.CLOSED,       ["_reset_state"]),
        "NO_EVENT":         (PRPState.RECOVERY,     []),
    },

    # -------------------------------------------------
    # FIN_WAIT
    # -------------------------------------------------
    PRPState.FIN_WAIT: {
        "ACK": (PRPState.CLOSED,        []),
        "FIN": (PRPState.CLOSING,       []),
        "RST": (PRPState.CLOSED,        ["_reset_state"]),
        "NO_EVENT": (PRPState.FIN_WAIT, []),
    },

    # -------------------------------------------------
    # CLOSING
    # -------------------------------------------------
    PRPState.CLOSING: {
        "ACK":      (PRPState.CLOSED,   []),
        "NO_EVENT": (PRPState.CLOSING,  []),
    },

    # -------------------------------------------------
    # CLOSED
    # -------------------------------------------------
    PRPState.CLOSED: {
        "SYN":      (PRPState.INIT,     []),
        "NO_EVENT": (PRPState.CLOSED,   []),
    },
}

def get_transition(current_state: PRPState, event: str):
    """
    Gibt zurück: (new_state, action_list)
    Falls nicht definiert → bleibt im aktuellen State, keine Actions
    """
    try:
        return STATE_TABLE[current_state][event]
    except KeyError:
        logger.debug(f"PRP State [{current_state.value}]: Unbehandelter Event '{event}' – bleibe im State")
        return current_state, []
