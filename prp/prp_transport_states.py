from enum import Enum
from cfg.logger_config import logger

class PRPState(Enum):
    CLOSED      = "CLOSED"      # Initial / nach RST/FIN
    INIT        = "INIT"        # Warte auf erstes Paket
    SYN_SENT    = "SYN_SENT"    #
    SYN_RCVD    = "SYN_RCVD"    #
    ESTABLISHED = "ESTABLISHED" # Normale Datenübertragung
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
    PRPState.INIT: {
        "DATA":         (PRPState.ESTABLISHED, ["_handle_first_data"]),  # Erstes DATA → direkt ESTABLISHED
        #"SYN":          (PRPState.SYN_RCVD, []),
        "SYN_SENT":     (PRPState.SYN_SENT, []),  # Interner Event nach senden
        "SYN_ACK":      (PRPState.ESTABLISHED, []),  # Empfange SYN als ACK
        "RST":          (PRPState.CLOSED, ["_reset_state"]),
        "NO_EVENT":     (PRPState.INIT, []),
    },

    PRPState.SYN_SENT: {
        "SYN":      (PRPState.ESTABLISHED, []),
        "SYN_ACK":  (PRPState.ESTABLISHED, []),  # Empfange SYN als ACK
        "DATA":     (PRPState.ESTABLISHED, ["_handle_first_data"]),
        "NO_EVENT": (PRPState.SYN_SENT, []),
        "TIMER_RETRY": (PRPState.SYN_SENT, ["_retry_syn"]),  # Neu: Retry SYN
    },

    PRPState.SYN_RCVD: {
        "SYN":      (PRPState.ESTABLISHED, []),
        "SYN_ACK":  (PRPState.ESTABLISHED, []),  # Empfange SYN als ACK
        "DATA":     (PRPState.ESTABLISHED, ["_handle_first_data"]),
        "NO_EVENT": (PRPState.ESTABLISHED, []),
    },

    PRPState.ESTABLISHED: {
        "ACK":              (PRPState.ESTABLISHED, []),
        "NACK":             (PRPState.ESTABLISHED, []),
        "DATA":             (PRPState.ESTABLISHED, []),
        "FIN":              (PRPState.FIN_WAIT, []),
        "RST":              (PRPState.CLOSED, ["_reset_state"]),
        "NO_EVENT":         (PRPState.ESTABLISHED, []),
        "TIMER_RETRY":      (PRPState.ESTABLISHED, ["_retry_pending"]),
    },

    PRPState.FIN_WAIT: {
        "DATA":     (PRPState.FIN_WAIT,    ["_send_ack"]),
        "ACK":      (PRPState.CLOSED,      []),  # FIN bestätigt → schließen
        "NACK":     (PRPState.FIN_WAIT,    []),
        "FIN":      (PRPState.CLOSING,     ["_send_ack"]),
        "RST":      (PRPState.CLOSED,      ["_reset_state"]),
        "ERROR":    (PRPState.CLOSED,      []),
        "RNR":      (PRPState.FIN_WAIT,    ["_pause_transmission"]),
        "NO_EVENT": (PRPState.FIN_WAIT,    []),
    },

    PRPState.CLOSING: {
        "ACK":      (PRPState.CLOSED,      []),
        "NACK":     (PRPState.CLOSING,     []),
        "NO_EVENT": (PRPState.CLOSING,     []),
    },

    PRPState.CLOSED: {
        # Alles ignorieren außer evtl. neuem SYN
        "DATA":     (PRPState.CLOSED,      []),
        "ACK":      (PRPState.CLOSED,      []),
        "NACK":     (PRPState.CLOSED,      []),
        "SYN":      (PRPState.INIT,        []),
        "NO_EVENT": (PRPState.CLOSED,      []),
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
