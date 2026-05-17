# prp/prp_transport_layer.py
"""
PRP Transport Layer – Zuverlässiger Transport über PRP
- Handhabt ACK/NACK mit selektivem Bitmuster
- Seq-Tracking, Reordering, Retrys
- Selektiv pro OPT-ID aktivierbar
- Dynamisch anpassbar (z. B. per Verbindungstyp)
"""
import time
from datetime import datetime
from cfg.logger_config import logger
from classes.CLbuffers import ListBuffer, ByteArrayBuffer, LockedDict
from prp.prp_const import PRP_OPT_PRP_ADMIN, PRP_OPT_L3_DATA, PRP_OPT_L3_ACK, PRP_OPT_L3_SYN, PRP_OPT_L3_FIN, \
    PRP_OPT_L3_RST, PRP_OPT_L3_ERROR, PRP_OPT_ESC_CLI
from prp.prp_l3.prp_transport_states import PRPState, get_transition


class PRPTransportLayer:
    def __init__(self, prp_root, adapter):
        self._prp_root    = prp_root
        self._adapter     = adapter
        # === Sequenz-Zähler: pro UID + Prio
        # prio → current_seq
        self._seq_counter = {True: 0, False: 0}

        # === State-Tracking: pro UID + Prio
        # prio → state_dict
        self._state =  {
            True:  self._default_state(),  # Prio-Kanal
            False: self._default_state()   # Nicht-Prio-Kanal
        }

        # Welche OPT-IDs nutzen L3
        self._transport_opt_ids = {
            PRP_OPT_L3_DATA:    True,
            PRP_OPT_L3_ACK:     True,
            PRP_OPT_L3_SYN:     True,
            PRP_OPT_L3_FIN:     True,
            PRP_OPT_L3_RST:     True,
            PRP_OPT_L3_ERROR:   True,
            PRP_OPT_PRP_ADMIN:  True,
            PRP_OPT_ESC_CLI:    True,
        }

        # Dynamische Anpassung pro Verbindungstyp
        self._conn_type = 'ax25_l2'  # Default – später setzen, z. B. 'pr_mail', 'aprs'
        self._config_per_type = {
            'ax25_l2': {
                'use_transport': True,
                'retry_limit': 1000,
                'retry_timer': 0.8,  # Sekunden
                'timeout': 1800,  # Verbindung-Timeout Sekunden
                'pac_size': 180,
                'window_size': 128,
                'keepalive_interval': 600,  # Sekunden
                'ack_mode': 'always',  # 'always', 'on_end', 'on_request'
                'ack_delay': 0.08,
            },
            'ax25_l3': {
                'use_transport': False,

            },

            'pr_mail': {
                'use_transport': True,
                'retry_limit': 0,  # Kein Retry – PR-Mail hat eigene Logik
                'retry_timer': 0,  # Sekunden
                'timeout': 604800,  # 1 Woche
                'pac_size': 8000,
                'window_size': 8,
                'keepalive_interval': 86400,  # 1 Tag
                'ack_mode': 'on_end',  # Nur bei letztem Fragment
                'ack_delay': 0.06,

            },
            'aprs': {
                'use_transport': True,  # APRS unreliable
                'retry_limit': 3,
                'retry_timer': 600,  # Sekunden
                'timeout': 3600,
                'pac_size': 100,
                'window_size': 32,
                'keepalive_interval': 800,
                'ack_mode': 'on_end',
                'ack_delay': 0.5,

            }
        }

        # Pro UID + Prio ein eigener State
        self._l3_state = {
            True: PRPState.INIT,
            False: PRPState.ESTABLISHED,
        }

    @staticmethod
    def _default_state():
        return {
            'expected_seq': 0,                   # Nächste erwartete SEQ
            'tx_buffer':   ListBuffer(),         # FIFO: [(opt_id, data, pac_size, callback)]
            'recv_buffer': ListBuffer(),         # list für sort() (SEQ, Data)
            'fragment_buffer': ByteArrayBuffer(),# Defragmentierte Daten bei vollständiger SEQ
            'waiting_for_end': False,            # Daten sind in mehreren L3-Paketen gesplittet, warte auf das letzte Paket
            'paused': False,                     # RNR
            'pending': LockedDict(),  # seq → pending      # TX: Pending
            'last_seen': datetime.now(),
            'last_keepalive': datetime.now(),

            'syn_retry_in_progress': False,
            'flush_lock': False,  # Lock während Flush/Retry

            'ack_pending':  False,  # ACK sammeln
            'nack_pending': False,  # NACK sammeln (Priorität)
            'ack_delay_timer': 0.0, # Timestamp des letzten Daten Frames
            'last_request_ts': 0,   # (falls du später on_request erweiterst)

            'last_delivered_end_seq': None,
            'awaiting_batch_ack': False,
        }

    def set_conn_type(self, conn_type):
        self._conn_type = conn_type
        logger.info(f"PRP Transport: Verbindungstyp auf {conn_type} geändert")

    @property
    def adapter(self):
        return self._adapter

    @property
    def use_transporter(self):
        return self._config_per_type[self._conn_type].get('use_transport')

    def is_transport_enabled(self, opt_id):
        if opt_id not in self._transport_opt_ids:
            return False
        config = self._config_per_type.get(self._conn_type, {'use_transport': False})
        return config['use_transport'] and self._transport_opt_ids[opt_id]

    def enable_for_opt_id(self, opt_id, enable=True):
        self._transport_opt_ids[opt_id] = enable
        logger.info(f"PRP Transport: OPT-ID {opt_id} {'aktiviert' if enable else 'deaktiviert'}")

    def _get_config_param(self, param_key: str):
        return self._config_per_type[self._conn_type].get(param_key)

    # ===================================================================
    def get_tx_cache_len(self, prio):
        return self._state[prio]['tx_buffer'].length

    # ===================================================================
    # Tasker
    # ===================================================================
    def tasker(self):
        """Wird alle ~10ms aufgerufen"""
        self._adapter.tasker()

        # Verbindung noch nicht aufgebaut
        if self._get_l3_state(True) != PRPState.ESTABLISHED:
            self._transition_conn("TIMER_RETRY")
            return

        for prio in [True, False]:
            self._transition(prio, "NO_EVENT")

            if self._get_l3_state(prio) != PRPState.ACK_WAIT:
                self._transition(prio, "TIMER_RETRY")
                continue

            # Delayed ACK/NACK Handling
            state = self._state[prio]
            if state['ack_pending'] or state['nack_pending']:
                self._send_delayed_ack_nack(prio)

            # ACK-REQUEST Retry
            if state['awaiting_batch_ack']:
                delay = self._get_config_param('ack_delay')
                if time.time() - state['last_request_ts'] > delay:
                    self._send_ack_request(prio)
                    state['last_request_ts'] = time.time()

            # Retry
            retry_timer = self._get_config_param('retry_timer')
            retry_due = any(
                time.time() - p['last_send'] > retry_timer
                for p in state['pending'].values()
            )
            if retry_due:
                self._transition(prio, "TIMER_RETRY")
            elif not state['pending']:

                # Flush TX Buffer
                self._flush_tx_buffer(prio)


    # ===================================================================
    # Handshake
    # ===================================================================
    def send_l3_handshake(self):
        if self._get_l3_state(prio=True) == PRPState.INIT:
            logger.debug("PRP L3: Send handshake – sende SYN")
            self._send_SYN(response=False, cmd=True)
            self._transition_conn(event="SYN_SENT")

    # ===================================================================
    # Senden (Client)
    # ===================================================================
    def send_reliable(self, opt_id, data, prio, pac_size=None, callback=None):
        """Neue API-Methode: Buffert immer, priorisiert Retries."""
        if not self.is_transport_enabled(opt_id):
            return self._prp_root.prp_tx(opt_id, tx_flag=True, data=data, prio=prio)

        if self._get_l3_state(True) == PRPState.INIT:
            logger.debug("PRP L3: Lazy handshake – sende SYN")
            self._send_SYN(response=False, cmd=True)
            self._transition_conn("SYN_SENT")

        # Immer buffer – interne Logik handhabt Priorisierung
        self._buffer_tx(prio, data, pac_size, callback)
        logger.debug(f"PRP L3: Neue Daten ({len(data)} Bytes) buffered – Retries priorisiert")
        return True # Keine SEQ sofort, da buffered

    def _send_data(self, data, prio, pac_size=None, callback=None):

        state    = self._state[prio]
        #if state['flush_lock']:
        #    logger.debug("PRP L3: Flush locked – warte auf Retry/Flush")
        #    self._buffer_tx(prio, opt_id, data, pac_size, callback)
        #    return None

        if self._get_l3_state(True) == PRPState.INIT:
            logger.debug("PRP L3: Lazy handshake – sende SYN")
            self._send_SYN(response=False, cmd=True)
            self._transition_conn(event="SYN_SENT")

        if state.get('paused'):
            logger.debug("PRP L3: Senden pausiert (RNR)")
            #self._buffer_tx(prio, opt_id, data, pac_size, callback)
            return None

        if self._get_l3_state(True) not in (PRPState.INIT, PRPState.ESTABLISHED):
            logger.warning(f"PRP L3: Senden in State {self._get_l3_state(True).value} nicht erlaubt")
            #self._buffer_tx(prio, opt_id, data, pac_size, callback)
            return None

        if self._get_l3_state(prio=prio) == PRPState.RECOVERY:
            logger.debug("PRP L3: NACK aktiv – neue DATA zurückgestellt")
            #self._buffer_tx(prio, opt_id, data, pac_size, callback)
            return None

        window = min(self._get_config_param('window_size'), 128)
        if len(state['pending'].keys()) >= window:
            #logger.debug("PRP L3: Window voll – warte")
            #self._buffer_tx(prio, opt_id, data, pac_size, callback)
            return None

        state = self._state[prio]
        if pac_size is None:
            pac_size = self._get_config_param('pac_size')

        payload_chunks: list = self._build_packets_fm_payload(prio=prio, pac_size=pac_size, data=data)

        #print(f"payload: {data}")
        #print(f"payload len: {len(data)}")
        #print(f"payload_chunks: {payload_chunks}")
        #print(f"payload_chunks len: {len(payload_chunks)}")
        seq_list = []
        for seq, prp_l3_data_pack in payload_chunks:
            success        = self._prp_root.prp_tx_l3(l3_opt_id=PRP_OPT_L3_DATA, l3_frame=prp_l3_data_pack, prio=prio)

            if success:
                if seq in state['pending'].keys():
                    raise OverflowError
                state['pending'].add(seq, {
                    'l3_pack'       : prp_l3_data_pack,
                    'l3_opt_id'     : PRP_OPT_L3_DATA,
                    'ts'            : datetime.now(),
                    'retries'       : 0,
                    'callback'      : callback or self._default_callback,
                    'last_send'     : time.time()
                })
                seq_list.append(seq)
        logger.debug(f"PRP-Send [{self._prp_root.uid}]: Pending states: {state['pending'].keys()}")
        return seq_list

    def _flush_tx_buffer(self, prio: bool):
        state = self._state[prio]

        if state.get('nack_pending'):
            return  # Warte auf NACK-Auflösung


        # Neu: Lock während Flush
        if state['flush_lock']:
            return
        state['flush_lock'] = True
        try:
            # Zuerst Retries (priorisiert)
            self._retry_pending(prio)

            # Dann tx_buffer leeren
            while not state['tx_buffer'].is_empty:
                data, pac_size, callback = state['tx_buffer'].buffer_get[0]

                # == Check PRP TX-Buffer
                packets = int(len(data) / (pac_size - 8))
                pack_free_in_buffer = self._prp_root.prp_tx_buffer.l3_pack_to_send
                if pack_free_in_buffer < packets:
                    logger.debug(f"PRP L3 [{self._prp_root.uid}]: Kein Platz für Datenpaket im PRP TX_Buffer - Free: {pack_free_in_buffer} / Need: {packets}")
                    break

                seqs = self._send_data(data=data, prio=prio, pac_size=pac_size, callback=callback)
                if seqs is None:
                    break
                state['tx_buffer'].buffer_pop(0)
        finally:
            state['flush_lock'] = False

    def _buffer_tx(self, prio, data, pac_size, callback):
        self._state[prio]['tx_buffer'].buffer_write(
            (data, pac_size, callback)
        )
        logger.debug(f"PRP L3: TX buffered ({len(data)} Bytes)")

    def _build_packets_fm_payload(self, data: bytes, pac_size: int, prio: bool):
        """ Zerlegt Payload in Chunks und baut PRP-L3-Data Frame """
        flag1       = prio
        packet_list = []
        pac_size    = pac_size - 8 # - l3 Header - Data + prp-l3 Header + crc
        while len(data) > pac_size :
            data_chunk = data[:pac_size]
            data       = data[pac_size:]
            # flag2 = more_follow
            seq          = self._get_current_seq_and_increment(prio)
            l3_data_pack = self._build_l3_pack_w_seq(seq, data_chunk, l3_opt_id=PRP_OPT_L3_DATA, flag1=flag1, flag2=True)
            packet_list.append((seq, l3_data_pack))

        # flag2 = more_follow
        if data:
            seq          = self._get_current_seq_and_increment(prio)
            l3_data_pack = self._build_l3_pack_w_seq(seq, data, l3_opt_id=PRP_OPT_L3_DATA, flag1=flag1, flag2=False)
            packet_list.append((seq, l3_data_pack))
        return packet_list

    # ===================================================================
    # Empfangen & Verarbeiten (Server/Client)
    # ===================================================================
    def handle_transport_frame(self, unpacked_prp_opt: tuple, payload: bytes):
        """
        ══════════════════════════════════════════════════════════════════════════
        3. L3-Daten-Paket (OPT-ID 30)
        ══════════════════════════════════════════════════════════════════════════
        +--------+--------+--------+-------------+----------+---------------+----- ~ ---------+--------+--------+
        | FLAG   | FLAG   | OPTBYTE| LEN (2B LE) | SEQ (1B) | ORIG-OPT (1B) | PAYLOAD (orig)  | CRC16  | CRC16  |
        | 0x8D   | 0x81   |   30   | LSB  MSB    |          |               | (var, ohne Len) | low    | high   |
        +--------+--------+--------+-------------+----------+---------------+----- ~ ---------+--------+--------+

        ══════════════════════════════════════════════════════════════════════════
        4. L3-ACK-Paket (OPT-ID 31)
        ══════════════════════════════════════════════════════════════════════════
        +--------+--------+--------+-------------+---------------+----- ~ --------------+--------+--------+
        | FLAG   | FLAG   | OPTBYTE| LEN (2B LE) | NEXT_SEQ (1B) | BITMASK (var, 0–32B) | CRC16  | CRC16  |
        | 0x8D   | 0x81   |   31   | LSB  MSB    |               |                      | low    | high   |
        +--------+--------+--------+-------------+---------------+----- ~ --------------+--------+--------+
            0        1        2        3      4         5         6 ...(5 + bitmask_len)    L+5     L+6
        """

        if len(payload) < 1:
            raise EncodingWarning("L3-Payload zu kurz")
        # Unpacked PRP-Opt
        opt_id, is_prio, more_follow = unpacked_prp_opt

        if opt_id == PRP_OPT_L3_SYN:
            """ 30 - SYN """
            #self._transition(is_prio, "SYN")
            self._process_SYN(payload, unpacked_prp_opt)

        elif opt_id == PRP_OPT_L3_ACK:
            """ 31 - ACK/NACK """
            # ACK oder NACK? Wir schauen später in _process_ACK rein
            self._process_ACK(payload, unpacked_prp_opt)

        elif opt_id == PRP_OPT_L3_FIN:
            """ 32 - FIN """
            self._transition_conn("FIN")
            self._process_FIN(payload, unpacked_prp_opt)

        elif opt_id == PRP_OPT_L3_RST:
            """ 33 - RST """
            self._transition_conn("RST")
            self._process_RST(payload, unpacked_prp_opt)

        elif opt_id == PRP_OPT_L3_ERROR:
            """ 34 - ERROR """
            self._transition_conn("ERROR")
            self._process_ERROR(payload, unpacked_prp_opt)

        elif opt_id == PRP_OPT_L3_DATA:
            """ 39 - DATA (PRP-DATA/Packets) """
            #self._transition(is_prio, "DATA")
            return self._process_DATA(payload, unpacked_prp_opt)

        else:
            logger.error(f"PRP L3: Unbekannte OPT-ID {opt_id}")

        # == Und wieder zurück zum PRP-Protocol-Processor
        #self._prp_root.prp_protocol.l3_decode_and_dispatch(opt_id=opt_id,
        #                                                   tx=origin_is_tx,
        #                                                   payload=data)
        return b''

    # ===================================================
    # ==== Data handling
    # ===================================================
    # == DATA
    def _handle_first_data(self, prio: bool):
        """
        Wird beim ersten empfangenen DATA-Paket in INIT oder SYN_SENT aufgerufen.
        Initialisiert den L3-Zustand und triggert ggf. ACK.
        """

        logger.info(
            f"PRP L3 [{self._prp_root.uid}] "
            f"{'Prio' if prio else 'NoPrio'}: Erstes DATA empfangen – wechsle zu ESTABLISHED"
        )
        state = self._state[prio]
        # Reset von Altlasten (wichtig bei Reconnects)
        state['recv_buffer'].buffer_clear()
        state['fragment_buffer'].buffer_clear()
        state['waiting_for_end'] = False
        state['paused'] = False
        state['last_seen'] = datetime.now()

        # ACK-Politik: optional sofort bestätigen
        state['ack_pending'] = True
        self._reset_ack_delay(prio)
        if self._get_l3_state(prio) != PRPState.ACK_WAIT:
            self._transition(prio, "START_ACK_WAIT")

    def _process_DATA(self, payload, unpacked_prp_opt):
        opt_id, prio, more_follow = unpacked_prp_opt

        # Sicherstellen, dass der State-Übergang passiert ist
        # (wird bereits in handle_transport_frame gemacht, aber für Klarheit)
        #self._transition(prio, "DATA")  # optional, da schon oben


        state  = self._state[prio]
        config = self._config_per_type[self._conn_type]

        if len(payload) < 1:
            logger.warning(f"PRP L3 [{self._prp_root.uid}]: Ungültiges Daten-Paket (zu kurz) – sende NACK")
            self._send_nack(prio)
            return b''

        seq           = int(payload[0])
        fragment_data = payload[1:]
        window_size   = min(config.get('window_size', 128), 128)
        logger.debug(f"PRP L3 [{self._prp_root.uid}] Prio={prio}: Empfangen SEQ={seq}, expected={state['expected_seq']}, more_follow={more_follow}")


        # Sequenz-Prüfung
        if seq == state['expected_seq']:
            logger.debug(f"PRP L3 [{self._prp_root.uid}]: SEQ korrekt – verarbeite Fragment")
            recv_buffer = state['recv_buffer'].buffer_get_and_lock
            if seq not in [s for s, _, _ in recv_buffer]:
                recv_buffer.append((seq, fragment_data, more_follow))
                recv_buffer.sort(
                    key=lambda x: (x[0] - state['expected_seq']) % 256
                )
            state['recv_buffer'].buffer_set_and_unlock(recv_buffer)
            state['ack_pending']    = True
            self._reset_ack_delay(prio)

            # ! ACK_WAIT nur starten, wenn wir nicht schon drin sind
            if self._get_l3_state(prio) != PRPState.ACK_WAIT:
                # ACK je nach ack_mode
                if config['ack_mode'] == 'always':
                    self._transition(prio=prio, event="START_ACK_WAIT")
                elif config['ack_mode'] == 'on_end' and not more_follow:
                    self._transition(prio=prio, event="START_ACK_WAIT")

            # on_request: Nur bei Anforderung (z. B. Keep-Alive)
            return self._process_buffer(prio)

        forward_dist = (seq - state['expected_seq']) % 256
        backward_dist = (state['expected_seq'] - seq) % 256

        # ===============================
        # 1. OUT-OF-ORDER (zukünftiges Fenster)
        # ===============================
        if forward_dist < window_size:
            logger.debug(
                f"PRP L3 [{self._prp_root.uid}]: "
                f"Out-of-order SEQ {seq} (forward_dist={forward_dist}) – puffere"
            )

            recv_buffer = state['recv_buffer'].buffer_get_and_lock
            if seq not in [s for s, _, _ in recv_buffer]:
                recv_buffer.append((seq, fragment_data, more_follow))
                recv_buffer.sort(
                    key=lambda x: (x[0] - state['expected_seq']) % 256
                )
            state['recv_buffer'].buffer_set_and_unlock(recv_buffer)

            # ➜ NACK erforderlich
            state['nack_pending'] = True
            state['ack_pending'] = False
            self._reset_ack_delay(prio)

            if self._get_l3_state(prio) != PRPState.ACK_WAIT:
                self._transition(prio=prio, event="START_ACK_WAIT")

        # ===============================
        # 2. DUPLICATE (nur nahes Backward)
        # ===============================
        elif backward_dist < window_size:
            logger.debug(
                f"PRP L3 [{self._prp_root.uid}]: "
                f"Duplicate SEQ {seq} (backward_dist={backward_dist}) – ACK"
            )

            state['ack_pending'] = True
            self._reset_ack_delay(prio)

            # ❗ ACK_WAIT nur starten, wenn wir nicht schon drin sind
            if self._get_l3_state(prio) != PRPState.ACK_WAIT:
                self._transition(prio=prio, event="START_ACK_WAIT")

        # ===============================
        # 3. FINAL VERALTET → DROP
        # ===============================
        else:
            logger.warning(
                f"PRP L3 [{self._prp_root.uid}]: "
                f"SEQ {seq} endgültig veraltet "
                f"(expected={state['expected_seq']}, backward_dist={backward_dist}) – DROP"
            )
            # KEIN ACK
            # KEIN NACK
            # KEIN ACK_WAIT

        return b''

    def _process_buffer(self, prio):
        state = self._state[prio]
        #logger.debug(f"_process_buffer recv_buffer: {state['recv_buffer']}")
        ret         = bytearray()

        while not state['recv_buffer'].is_empty:
            try:
                next_seq, fragment_data, more_follow = tuple(state['recv_buffer'].buffer_get[0])
            except IndexError:
                break
            if next_seq == state['expected_seq']:
                state['recv_buffer'].buffer_pop(0)
                ret += self._handle_received_fragment(prio, fragment_data, more_follow)
                state['expected_seq'] = (state['expected_seq'] + 1) % 256
                #self._send_ack(uid, prio)
            else:
                break
        return ret


    def _handle_received_fragment(self, prio, fragment_data, more_follow):
        state = self._state[prio]
        #logger.debug(f"_handle_received_fragment: uid:{self._prp_root.uid}, prio:{prio}, fragment_data:{fragment_data}, more_follow:{more_follow}")
        # Fragment anhängen
        state['fragment_buffer'].buffer_write(fragment_data)

        if more_follow:
            # Mehr folgt → warten
            state['waiting_for_end'] = True
            logger.debug(
                f"PRP L3 [{self._prp_root.uid}]: Fragment empfangen (mehr folgt), Buffer: {state['fragment_buffer'].length} Bytes")
            return b''

        # === END-FRAGMENT ===
        end_seq = (state['expected_seq'] - 1) % 256

        if state['last_delivered_end_seq'] == end_seq:
            logger.warning(
                f"PRP L3 [{self._prp_root.uid}]: DUPLICATE end fragment SEQ={end_seq} – ignore"
            )
            state['fragment_buffer'].buffer_clear()
            state['waiting_for_end'] = False
            return b''

        state['last_delivered_end_seq'] = end_seq

        # Letztes Fragment
        full_payload = bytes(state['fragment_buffer'].buffer_get)

        # Buffer zurücksetzen
        state['fragment_buffer'].buffer_clear()
        state['waiting_for_end'] = False

        logger.info(f"PRP L3 [{self._prp_root.uid}]: Komplettes Paket rekonstruiert – {len(full_payload)} Bytes")

        # Weiterleiten an normale PRP-Verarbeitung
        try:
            return self._prp_root.prp_protocol.l3_decode_and_dispatch(full_payload)
        except Exception as e:
            logger.error(f"PRP L3 [{self._prp_root.uid}]: Fehler beim Dispatch rekonstruierten Pakets: {e}")

        return b''

    # ===================================================
    # ==== CTRL
    # ===================================================
    # == ACK
    def _process_ACK(self, payload, unpacked_prp_opt: tuple):
        logger.debug(f"PRP L3 [{self._prp_root.uid}]: Process ACK – unpacked_prp_opt={unpacked_prp_opt} - payload={payload}")
        opt_id, prio, is_cmd = unpacked_prp_opt
        if is_cmd:
            # ACK-REQUEST
            self._handle_ack_request(prio)
            return None

        state: dict = self._state[prio]

        parsed = self._parse_ack_nack(payload)
        if parsed[0] is None:
            return None

        next_expected, bitmask_len, bitmask = parsed
        # ACK clears batch wait
        state['awaiting_batch_ack'] = False

        # == 1. ACK-Teil: alles < next_expected ist bestätigt
        for s in list(state['pending'].keys()):
            if self._is_acked(s, next_expected):
                logger.warning(
                    f"PRP L3 [{self._prp_root.uid}]: "
                    f"Dropping stale pending SEQ={s}"
                )
                pending = state['pending'].pop(s)
                if pending.get('callback'):
                    pending['callback'](success=False)

        # == 2. Reines ACK?
        if bitmask_len == 0:
            # ACK: Alles OK bis next_expected
            logger.debug(f"PRP L3 [{self._prp_root.uid}]: Process ACK – ACK: Alles OK bis next_expected")
            self._transition(prio, "ACK")
            return None

        # == 3. NACK: Bitmask parsen
        logger.debug(f"PRP L3 [{self._prp_root.uid}]: Process ACK – NACK: Bitmask parsen")
        self._log_bitmask_table(prio, next_expected, bitmask, "Process NACK", tx=False)

        missing = False
        for i in range(bitmask_len * 8):
            if not (bitmask[i // 8] & (1 << (i % 8))):
                missing_seq = (next_expected + i) % 256
                if missing_seq in state['pending'].keys():
                    logger.debug(f"PRP L3 [{self._prp_root.uid}]: Process ACK – ReTry-SEQ: {missing_seq}")
                    self._retry_packet(missing_seq, prio)
                    missing = True

        #self._transition(prio, "NACK")
        if missing:
            self._transition(prio,"ENTER_RECOVERY")
        else:
            self._transition(prio,"EXIT_RECOVERY")

        logger.debug(f"Pending keys für uid {self._prp_root.uid}: {list(state['pending'].keys())}")
        # state['last_ack'] = next_expected
        return None

    @staticmethod
    def _is_acked(seq, next_expected):
        # seq < next_expected (mod 256)
        return (seq - next_expected) % 256 >= 128

    def _handle_ack_request(self, prio):
        state = self._state[prio]

        if state['recv_buffer'].is_empty:
            self._send_ack(prio, response=True)
        else:
            self._send_nack(prio, response=True)
        # ACK-WAIT hier NICHT betreten

    # == SYN
    def _process_SYN(self, payload, unpacked_prp_opt):
        opt_id, prio, more = unpacked_prp_opt
        logger.info(f"PRP L3 [{self._prp_root.uid}]: SYN empfangen")

        if self._get_l3_state(prio=True) == PRPState.INIT:
            self._send_SYN(response=True, cmd=False)  # SYN-ACK
            self._transition_conn("SYN_ACK")

        elif self._get_l3_state(prio=True) == PRPState.SYN_SENT:
            self._transition_conn("SYN_ACK")

        elif self._get_l3_state(prio=True) == PRPState.ESTABLISHED:
            self._send_SYN(response=True, cmd=False)  # SYN-ACK
            self._transition_conn("SYN_ACK")

        #self._flush_tx_buffer(prio)
        return None

    # == FIN
    def _process_FIN(self, payload, unpacked_prp_opt: tuple):
        logger.debug(f"PRP L3 [{self._prp_root.uid}]: FIN RECV – unpacked_prp_opt={unpacked_prp_opt} - payload={payload}")

    # == RST
    def _process_RST(self, payload, unpacked_prp_opt: tuple):
        opt_id, prio, more = unpacked_prp_opt
        logger.debug(f"PRP L3 [{self._prp_root.uid}]: RST RECV – unpacked_prp_opt={unpacked_prp_opt} - payload={payload}")
        self._transition_conn("RST")

    # == ERROR
    def _process_ERROR(self, payload, unpacked_prp_opt: tuple):
        logger.debug(f"PRP L3 [{self._prp_root.uid}]: ERROR RECV – unpacked_prp_opt={unpacked_prp_opt} - payload={payload}")
        return None

    # ===================================================================
    # ACK/NACK Senden (Server)
    # ===================================================================
    def _send_ack(self, prio, response=True):
        state         = self._state[prio]
        next_expected = state['expected_seq']
        payload = bytearray([0]) # Nur EIN Byte: bitmask_len = 0

        logger.debug(f"PRP L3 [{self._prp_root.uid}]: Sende ACK – next_expected={next_expected}")

        prp_l3_frame = self._build_l3_pack_w_seq(l3_opt_id=PRP_OPT_L3_ACK,
                                                 seq=next_expected,
                                                 flag1=prio,
                                                 flag2=response,
                                                 data=bytes(payload))

        self._prp_root.prp_tx_l3_ctrl(l3_opt_id=PRP_OPT_L3_ACK, l3_frame=prp_l3_frame, prio=True)
        #self._transition(prio, 'STOP_ACK_WAIT')

    def _send_ack_request(self, prio):
        logger.debug(
            f"PRP L3 [{self._prp_root.uid}]: Sende ACK-REQUEST"
        )

        prp_l3_frame = self._build_l3_pack_w_seq(
            l3_opt_id=PRP_OPT_L3_ACK,
            seq=self.get_current_seq(prio),
            flag1=prio,
            flag2=True,  # CMD = Request
            data=b'\x00'  # payload leer (bitmask_len = 0)
        )

        self._prp_root.prp_tx_l3_ctrl(
            l3_opt_id=PRP_OPT_L3_ACK,
            l3_frame=prp_l3_frame,
            prio=True
        )

    def _send_nack(self, prio, response=True):
        state = self._state[prio]
        recv_seqs = {t[0] for t in state['recv_buffer'].buffer_get}

        if not recv_seqs:
            self._send_ack(prio)
            return

        start_seq = state['expected_seq']
        max_seq = max(recv_seqs)

        # Korrekter Abstand im 256-Ring
        distance = (int(max_seq) - start_seq) % 256
        bitmask_len = (distance + 7) // 8 + 1 if distance > 0 else 1  # Mindestens 1 Byte

        bitmask = bytearray(bitmask_len)

        for seq in recv_seqs:
            seq_dist = (seq - start_seq) % 256
            if seq_dist < bitmask_len * 8:
                bitmask[seq_dist // 8] |= (1 << (seq_dist % 8))

        payload = bytearray([bitmask_len]) + bitmask

        logger.debug(f"PRP L3 [{self._prp_root.uid}]: Sende NACK – next={start_seq}, len={bitmask_len}")

        prp_l3_frame = self._build_l3_pack_w_seq(
            l3_opt_id=PRP_OPT_L3_ACK,
            seq=start_seq,
            flag1=prio,
            flag2=response,
            data=bytes(payload)
        )
        self._log_bitmask_table(prio, start_seq, bitmask, "Sende NACK")
        self._prp_root.prp_tx_l3_ctrl(l3_opt_id=PRP_OPT_L3_ACK, l3_frame=prp_l3_frame, prio=True)
        #self._transition(prio, 'STOP_ACK_WAIT')


    def _reset_ack_delay(self, prio: bool):
        state = self._state[prio]
        state['ack_delay_timer'] = time.time()

    def _send_delayed_ack_nack(self, prio: bool):
        state = self._state[prio]
        now   = time.time()
        delay = self._get_config_param('ack_delay')
        if not state['nack_pending'] and not state['ack_pending']:
            #self._transition(prio=prio, event="STOP_ACK_WAIT")
            return

        if now - state['ack_delay_timer'] < delay:
            return  # Noch zu früh

        if state['nack_pending']:
            self._send_nack(prio)
            logger.debug(f"PRP L3 [{self._prp_root.uid}]: Delayed NACK gesendet")
        elif state['ack_pending']:
            self._send_ack(prio)
            logger.debug(f"PRP L3 [{self._prp_root.uid}]: Delayed ACK gesendet")

        # Reset pending und Timestamp
        state['ack_pending']  = False
        state['nack_pending'] = False
        self._reset_ack_delay(prio)

        self._transition(prio=prio, event="STOP_ACK_WAIT")

    # ===================================================================
    # CTRL-Frames Senden (Server)
    # ===================================================================
    def _send_SYN(self, response=False, cmd=True):
        """
        l3_opt_id = PRP_OPT_L3_SYN
        Seq       = My Prio SEQ,
        Payload   = My No-Prio SEQ, Client Prio SEQ, Client No-Prio SEQ,
        (alle Ctrl-Frames als Prio)
        """
        l3_opt_id    = PRP_OPT_L3_SYN
        my_prio_seq     = self.get_current_seq(True)
        my_no_prio_seq  = self.get_current_seq(False)
        cl_prio_seq     = self._get_expected_client_seq(True)
        cl_no_prio_seq  = self._get_expected_client_seq(False)
        payload      = bytearray()
        payload      += int(my_no_prio_seq).to_bytes(1)
        payload      += int(cl_prio_seq).to_bytes(1)
        payload      += int(cl_no_prio_seq).to_bytes(1)
        prp_l3_frame = self._build_l3_pack_w_seq(l3_opt_id=l3_opt_id,
                                                 seq=my_prio_seq,
                                                 flag1=response,
                                                 flag2=cmd,
                                                 data=bytes(payload))
        self._prp_root.prp_tx_l3_ctrl(l3_opt_id=l3_opt_id, l3_frame=prp_l3_frame, prio=True)
        return None

    def _retry_syn(self, prio):
        state = self._state[prio]
        now = time.time()
        delay = self._get_config_param('ack_delay')
        if state['syn_retry_in_progress'] and now - state['ack_delay_timer'] < delay:
            return
        logger.info(f"PRP L3 [{self._prp_root.uid}]: Retry SYN (State SYN_SENT)")
        state['syn_retry_in_progress'] = True
        state['ack_delay_timer']       = now
        self._send_SYN(response=False, cmd=True)

    def _send_FIN(self, response=False, cmd=True):
        """
        l3_opt_id = PRP_OPT_L3_FIN
        Seq       = My Prio SEQ,
        Payload   = My No-Prio SEQ,
        (alle Ctrl-Frames als Prio)
        """
        l3_opt_id = PRP_OPT_L3_FIN
        prio_seq     = self.get_current_seq(True)
        no_prio_seq  = self.get_current_seq(False)
        payload      = int(no_prio_seq).to_bytes(1)
        prp_l3_frame = self._build_l3_pack_w_seq(l3_opt_id=l3_opt_id,
                                                 seq=prio_seq,
                                                 flag1=response,
                                                 flag2=cmd,
                                                 data=bytes(payload))
        self._prp_root.prp_tx_l3_ctrl(l3_opt_id=l3_opt_id, l3_frame=prp_l3_frame, prio=True)
        return None

    def _send_RST(self, response=False, cmd=True):
        """
        l3_opt_id = PRP_OPT_L3_RST
        Seq       = My Prio SEQ,
        Payload   = My No-Prio SEQ, Client Prio SEQ, Client No-Prio SEQ,
        (alle Ctrl-Frames als Prio)
        """
        l3_opt_id = PRP_OPT_L3_RST
        my_prio_seq    = self.get_current_seq(True)
        my_no_prio_seq = self.get_current_seq(False)
        cl_prio_seq    = self._get_expected_client_seq(True)
        cl_no_prio_seq = self._get_expected_client_seq(False)
        payload  = bytearray()
        payload += int(my_no_prio_seq).to_bytes(1)
        payload += int(cl_prio_seq).to_bytes(1)
        payload += int(cl_no_prio_seq).to_bytes(1)
        prp_l3_frame = self._build_l3_pack_w_seq(l3_opt_id=l3_opt_id,
                                                 seq=my_prio_seq,
                                                 flag1=response,
                                                 flag2=cmd,
                                                 data=bytes(payload))
        self._prp_root.prp_tx_l3_ctrl(l3_opt_id=l3_opt_id, l3_frame=prp_l3_frame, prio=True)
        return None

    def _send_ERROR(self, response=False, cmd=True):
        """
        l3_opt_id = PRP_OPT_L3_ERROR
        Seq       = My Prio SEQ,
        Payload   = My No-Prio SEQ, Client Prio SEQ, Client No-Prio SEQ,
        (alle Ctrl-Frames als Prio)
        """
        l3_opt_id = PRP_OPT_L3_ERROR
        my_prio_seq    = self.get_current_seq(True)
        my_no_prio_seq = self.get_current_seq(False)
        cl_prio_seq    = self._get_expected_client_seq(True)
        cl_no_prio_seq = self._get_expected_client_seq(False)
        payload  = bytearray()
        payload += int(my_no_prio_seq).to_bytes(1)
        payload += int(cl_prio_seq).to_bytes(1)
        payload += int(cl_no_prio_seq).to_bytes(1)
        prp_l3_frame = self._build_l3_pack_w_seq(l3_opt_id=l3_opt_id,
                                                 seq=my_prio_seq,
                                                 flag1=response,
                                                 flag2=cmd,
                                                 data=bytes(payload))
        self._prp_root.prp_tx_l3_ctrl(l3_opt_id=l3_opt_id, l3_frame=prp_l3_frame, prio=True)
        return None

    # ===================================================================
    # Retry (Client)
    # ===================================================================
    def _retry_packet(self, seq, prio):
        state   = self._state[prio]
        pending = state['pending'].get(seq)
        if not pending:
            return None
        if time.time() - pending['last_send'] < self._get_config_param('retry_timer'):
            return None

        if pending and pending['retries'] < self._config_per_type[self._conn_type]['retry_limit']:
            pending['retries'] += 1
            pending['last_send'] = time.time()
            self._prp_root.prp_tx_l3(l3_opt_id=pending['l3_opt_id'], l3_frame=pending['l3_pack'], prio=prio)
            logger.debug(f"PRP Transport [{self._prp_root.uid}]: Retry Seq {seq} (Versuch {pending['retries']})")
        elif pending:
            logger.error(f"PRP Transport [{self._prp_root.uid}]: Retry-Limit erreicht für Seq {seq}")
            if pending['callback']:
                pending['callback'](success=False)
            logger.error("Connection unstable – aborting transport")
            self._send_RST()
            self._transition_conn("RST")
            raise ConnectionError

        return None

    def _retry_pending(self, prio):
        for seq in list(self._state[prio]['pending'].keys()):
            self._retry_packet(seq, prio)
        return None

    # ===================================================================
    # Callback
    # ===================================================================
    @staticmethod
    def _default_callback(success):
        #logger.debug(f"PRP L3 Default Callback: success={success}")
        pass

    # ===================================================================
    # Hilfsfunktionen Testing
    # ===================================================================
    def set_current_seq(self, prio, seq: int):
        self._seq_counter[prio] = seq

    def _log_bitmask_table(self, prio: bool, next_expected: int, bitmask: bytes, comment: str = "", tx=True):
        """
        Loggt die Bitmask als verständliche Tabelle.
        bitmask: die reine Bitmask (ohne Längenbyte)
        next_expected: SEQ-Nummer, ab der die Bitmask gilt
        comment: optionaler Kommentar (z.B. 'Sende NACK' oder 'Process ACK')
        """
        state = self._state[prio]
        if tx:
            recv_seqs = {seq for seq, _, _ in state['recv_buffer'].buffer_get}
        else:
            recv_seqs = state['pending'].keys()

        comment_str = f" ({comment})" if comment else ""

        if len(bitmask) == 0:
            # Reines ACK: alles bis next_expected-1 empfangen
            logger.info(
                f"PRP L3 [{self._prp_root.uid}]{comment_str}: Reines ACK – alles bis SEQ {next_expected - 1} empfangen")
            return

        logger.info(
            f"PRP L3 [{self._prp_root.uid}]{comment_str}: Bitmask-Auswertung (next_expected={next_expected}, Länge={len(bitmask)} Bytes)")
        logger.info(f"PRP L3 [{self._prp_root.uid}]: BitMask-RAW: {bitmask} -  BitMask-HEX: {bitmask.hex()}")
        table_lines = []

        # Header: SEQ-Nummern
        header = "SEQ |"
        bits_line = "Bit |"
        status_line = "Stat|"

        total_bits = len(bitmask) * 8
        for i in range(total_bits):
            seq = (next_expected + i) % 256
            header += f" {seq:>3}"
            bit_val = (bitmask[i // 8] >> (i % 8)) & 1
            bits_line += f"  {bit_val} "
            received = seq in recv_seqs
            status_line += "  ✓ " if received else "  ✗ "

            if (i + 1) % 8 == 0:  # Nach jedem Byte Trennlinie
                header += " |"
                bits_line += " |"
                status_line += " |"

        table_lines.append(header)
        table_lines.append(bits_line)
        table_lines.append(status_line)

        logger.info("\n" + "\n".join(table_lines))

        # Zusammenfassung
        received = []
        missing = []
        for i in range(total_bits):
            seq = (next_expected + i) % 256
            if (bitmask[i // 8] >> (i % 8)) & 1:
                received.append(seq)
            else:
                missing.append(seq)

        logger.info(f"PRP L3 [{self._prp_root.uid}]{comment_str}: Empfangen: {received}")
        logger.info(f"PRP L3 [{self._prp_root.uid}]{comment_str}: Fehlend: {missing}")
    # ===================================================================
    # Hilfsfunktionen
    # ===================================================================
    def _get_expected_client_seq(self, prio):
        state = self._state[prio]
        return state['expected_seq']

    def get_current_seq(self, prio):
        return int(self._seq_counter[prio])

    def _get_current_seq_and_increment(self, prio):
        current_seq = self.get_current_seq(prio)
        self._seq_counter[prio] = (self._seq_counter[prio] + 1) % 256
        return current_seq

    def _build_l3_pack_w_seq(self, seq, data, l3_opt_id: int, flag1: bool, flag2: bool):

        return self._prp_root.prp_protocol.encode_l3_frame(l3_opt_id=l3_opt_id,
                                                           seq=seq,
                                                           flag1=flag1,
                                                           flag2=flag2,
                                                           data=data)

    @staticmethod
    def _parse_ack_nack(payload):
        if len(payload) < 2:
            logger.warning("PRP L3: ACK-Payload zu kurz – ignoriere")
            return None, None, None

        next_expected = payload[0]
        bitmask_len   = payload[1]

        if bitmask_len == 0:
            return next_expected, 0, b''

        if len(payload) < 2 + bitmask_len:
            logger.warning("PRP L3: ACK Bitmask unvollständig – ignoriere")
            return None, None, None

        bitmask = payload[2:2 + bitmask_len]
        return next_expected, bitmask_len, bitmask

    # ===================================================================
    # L3 State Hilfsfunktionen (Zustandsmaschine)
    # ===================================================================
    def _get_l3_state(self, prio):
        return self._l3_state[prio]

    def _set_l3_state(self, prio, new_state: PRPState):
        old = self._l3_state[prio]
        if old != new_state:
            logger.info(f"PRP L3 [{self._prp_root.uid}] [{prio}]: State {old.value} → {new_state.value}")
        self._l3_state[prio] = new_state

    def _execute_actions(self, prio: bool, actions: list):
        for action in actions:
            fn = getattr(self, action, None)
            if fn:
                fn(prio)
            else:
                logger.warning(f"PRP L3 [{self._prp_root.uid}]: Unbekannte Action '{action}' im State-Table")

    def _transition_conn(self, event):
        self._transition(True, event)

    def _transition(self, prio: bool, event: str):
        """
        Zentrale Zustandsübergangsfunktion
        Wird von handle_transport_frame, tasker() und später Timer aufgerufen
        """
        current = self._get_l3_state(prio=prio)
        new_state, actions = get_transition(current, event)

        self._set_l3_state(prio, new_state)
        return self._execute_actions(prio, actions)

    # Beispiel-Action für RNR (Receive Not Ready)
    def _pause_transmission(self, prio: bool):
        """Wird aufgerufen bei RNR – pausiert das Senden auf diesem Kanal"""
        state = self._state[prio]
        state.setdefault('paused', False)
        state['paused'] = True
        logger.info(f"PRP L3 [{self._prp_root.uid}] {'Prio' if prio else 'NoPrio'}: Übertragung pausiert (RNR empfangen)")
        return None

    # Optional: Gegenstück RR (Receive Ready) – später
    # def _resume_transmission(self, uid: str, prio: bool):
    #     state = self._state[uid][prio]
    #     state['paused'] = False
    #     logger.info(f"PRP L3 [{uid}]: Übertragung fortgesetzt (RR empfangen)")

    def get_all_pending(self):
        return self._state[True]['pending'].keys(), self._state[False]['pending'].keys()