# prp/prp_l3/prp_transport_adapter.py

from collections import deque
from cfg.logger_config import logger



class PRPTransportAdapter:
    """
    Vermittelt zwischen PRP-L3 und konkreten Transporten (AX25, PR-Mail, APRS, IP).
    Entscheidet WANN und ÜBER WELCHEN Transport gesendet wird.
    """

    def __init__(self):
        self._transports = []
        self._rr_index = 0

        # getrennte Queues für Prio
        self._ctrl_queue = deque()
        self._prio_queue = deque()
        self._data_queue = deque()

    # ==========================================================
    # Registration
    # ==========================================================

    def register_transport(self, transport):
        """
        transport muss bereitstellen:
        - send(frame) -> bool
        - is_ready() -> bool
        - tasker()
        - transport_type (str)
        """
        self._transports.append(transport)
        logger.debug(f"PRPAdapter: registered transport {transport.transport_type}")

    # ==========================================================
    # Public API (PRP-L3 / Scheduler)
    # ==========================================================

    def send(self, frame: bytes, prio: bool, ctrl: bool = False):
        """
        Nimmt Frame an, puffert es.
        """
        if ctrl:
            self._ctrl_queue.append(frame)
        elif prio:
            self._prio_queue.append(frame)
        else:
            self._data_queue.append(frame)

        return True

    def is_tx_allowed(self):
        """
        Kann aktuell irgendwas gesendet werden?
        """
        return any(t.is_ready() for t in self._transports)

    def tasker(self):
        """
        Zyklisch aufgerufen.
        """
        # Transport-Tasker
        for t in self._transports:
            t.tasker()

        # CTRL immer zuerst
        if self._ctrl_queue:
            self._dispatch(self._ctrl_queue, ctrl=True)
            return

        if self._prio_queue:
            self._dispatch(self._prio_queue, prio=True)
            return

        if self._data_queue:
            self._dispatch(self._data_queue)

    # ==========================================================
    # Internes Scheduling
    # ==========================================================

    def _dispatch(self, queue: deque, prio=False, ctrl=False):
        if not queue:
            return

        frame = queue[0]

        transport = self._select_transport(ctrl=ctrl)
        if not transport:
            return

        if transport.send(frame):
            queue.popleft()
        else:
            logger.debug("PRPAdapter: transport busy")

    def _select_transport(self, ctrl=False):
        """
        Auswahl je nach Transporttyp.
        """
        if not self._transports:
            return None

        # PR-Mail: sofort, kein RR
        for t in self._transports:
            if t.transport_type == 'pr_mail' and t.is_ready():
                return t

        # AX25 / APRS: Round Robin
        count = len(self._transports)
        for _ in range(count):
            t = self._transports[self._rr_index]
            self._rr_index = (self._rr_index + 1) % count
            if t.is_ready():
                return t

        return None


class MockAx25Transport:
    """
    Mock-Transport für PRP TestAPP.
    Simuliert AX25-L2 ohne echte Übertragung.
    """

    transport_type = 'ax25_l2'

    def __init__(self, name: str):
        self.name = name

        # Frames, die vom PRP gesendet wurden
        self._tx_queue = deque()

        # Optional: Busy-Simulation
        self._ready = True

    # ==========================================================
    # Interface für PRPTransportAdapter
    # ==========================================================

    def send(self, frame: bytes):
        """
        Wird vom PRPTransportAdapter aufgerufen.
        """
        if not self._ready:
            return False

        self._tx_queue.append(frame)
        logger.debug(
            f"[MockAx25:{self.name}] TX enqueue: {len(frame)} Bytes"
        )
        return True

    def is_ready(self):
        """
        AX25 ist halbduplex – hier aber immer bereit,
        da die TestAPP das Timing steuert.
        """
        return self._ready

    def tasker(self):
        """
        Kein eigenes Timing nötig.
        """
        pass

    # ==========================================================
    # TestAPP-Hilfsfunktionen
    # ==========================================================

    def get_TEST_payload_fm_tx_buffer(self):
        """
        Liefert alle gesendeten Frames zurück
        und leert den TX-Puffer.

        Rückgabeformat passend zu:
        sender.prp_tx_buffer.get_TEST_payload_fm_tx_buffer()
        """
        frames = []
        while self._tx_queue:
            frame = self._tx_queue.popleft()
            # opt_id wird von PRP gesetzt, hier egal
            frames.append((None, frame))
        return frames

    def set_ready(self, state: bool):
        """
        Optional: Simuliere Busy / Channel belegt
        """
        self._ready = bool(state)