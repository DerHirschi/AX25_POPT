from cfg.constant import APRS_IGATE_RATE_LIMIT
from cfg.popt_config import POPT_CFG
from cfg.logger_config import logger
from datetime import datetime
import time


class APRSiGate:
    def __init__(self, aprs_ais, port_handler):
        self._aprs_ais     = aprs_ais
        self._port_handler = port_handler

        # ====================
        # CFG
        igate_cfg                = POPT_CFG.get_CFG_aprs_igate()
        self._igate_active       = igate_cfg.get('igate_active',       True)  # Globaler Schalter
        self._igate_rf_to_is     = igate_cfg.get('igate_rf_to_is',     True)   # RF → IS (meist immer an)
        self._igate_is_to_rf     = igate_cfg.get('igate_is_to_rf',     True)  # IS → RF (vorsichtig!)
        self._igate_max_distance = igate_cfg.get('igate_max_distance', 80)     # km für IS→RF
        self._igate_local_time   = igate_cfg.get('igate_local_time',   45)     # Minuten, wie lange eine Station "lokal" gilt
        self._igate_ports        = igate_cfg.get('igate_ports',        [])     # Liste von Port-IDs, auf denen I-Gate aktiv sein soll (leer = alle)
        self._igate_dup_time     = igate_cfg.get('igate_dup_time',     30)     # Block Duplicate Packet for x sec.

        ais_cfg                  = POPT_CFG.get_CFG_aprs_ais()
        self._igate_call         = ais_cfg.get('ais_call', '').upper()
        # ====================
        if not self._igate_call:
            logger.info("APRS-IGate: No APRS Station (Call) configured yet. APRS-IGate disabled!")
            self._igate_active = False
        # ====================
        self._dupe_cache = {}
        self._tx_counter = []
        # ====================
        self._get_node_tab = lambda : self._aprs_ais.get_node_tab()

    def reinit(self):
        # ====================
        # CFG
        ais_cfg = POPT_CFG.get_CFG_aprs_igate()

        self._igate_active       = ais_cfg.get('igate_active',       True)  # Globaler Schalter
        self._igate_rf_to_is     = ais_cfg.get('igate_rf_to_is',     True)   # RF → IS (meist immer an)
        self._igate_is_to_rf     = ais_cfg.get('igate_is_to_rf',     True)  # IS → RF (vorsichtig!)
        self._igate_max_distance = ais_cfg.get('igate_max_distance', 80)     # km für IS→RF
        self._igate_local_time   = ais_cfg.get('igate_local_time',   45)     # Minuten, wie lange eine Station "lokal" gilt
        self._igate_ports        = ais_cfg.get('igate_ports',        [])     # Liste von Port-IDs, auf denen I-Gate aktiv sein soll (leer = alle)

        ais_cfg          = POPT_CFG.get_CFG_aprs_ais()
        self._igate_call = ais_cfg.get('ais_call', '').upper()

    ##########################
    # I-Gate Helper
    def should_gate_to_is(self, aprs_pack: dict):
        if not (self._igate_active and self._igate_rf_to_is):
            return False, None

        port_id = aprs_pack.get('port_id', '')
        if str(port_id) not in map(str, self._igate_ports):
            return False, None

        packet_format = aprs_pack.get('format', '')
        via  = aprs_pack.get('via', '') or ''
        path = aprs_pack.get('path', [])

        # =========================
        # 1. Internet Müll raus filtern
        # =========================
        if any(x in via.upper() for x in ['TCPIP', 'TCPXX', 'qAR', 'qAO', 'qAC']):
            return False, None

        if any(p.upper() in ['TCPIP', 'TCPXX', 'NOGATE', 'RFONLY'] for p in path):
            return False, None

        # =========================
        # 2. Thirdparty unwrap
        # =========================
        if packet_format == 'thirdparty':
            aprs_pack = self._unwrap_thirdparty(aprs_pack)
            if not aprs_pack:
                return False, None

            # OPTIONAL STRICT MODE:
            # Wenn du KEIN Re-Gating willst:
            # return False, None

            # sonst weiter verarbeiten → qAO später

            # Update nach unwrap
            path = aprs_pack.get('path', [])
            # via = aprs_pack.get('via', '') or ''

        # =========================
        # 3. Nur "echte RF Pakete"
        # =========================
        if not any('*' in p for p in path):
            return False, None

        # =========================
        # 4. Rate Limit
        # =========================
        if not self._allow_tx():
            return False, None

        # =========================
        # 5. Duplikate
        # =========================
        raw = aprs_pack.get('raw', '')
        if self._is_duplicate(raw):
            return False, None

        # =========================
        # 6. Queries raus
        # =========================
        if packet_format == 'query' or aprs_pack.get('raw_message_text', '').startswith('?'):
            return False, None

        # =========================
        # 7. Ungültige Calls
        # =========================
        from_call = aprs_pack.get('from', '').upper()
        if from_call.startswith(('WIDE', 'RELAY', 'TRACE', 'NOCALL', 'N0CALL')):
            return False, None

        # =========================
        # 8. Eigene Calls
        # =========================
        """
        to_call = aprs_pack.get('addresse', '').upper()
        if (to_call in POPT_CFG.get_stat_CFG_keys() or
                from_call in POPT_CFG.get_stat_CFG_keys()):
            logger.info("APRS I-Gate: To/From Call is own Station. No I-Gating...")
            return False, None
        """

        # =========================
        # OK → darf ins IS
        # =========================
        return True, aprs_pack

    def should_gate_to_rf(self, aprs_pack: dict):
        """Entscheidet, ob ein Paket vom APRS-IS auf RF gesendet werden soll.
           Sehr restriktiv! Standard ist nur Messages + Positions von lokalen Stationen."""
        if not (self._igate_active and self._igate_is_to_rf):
            return False

        packet_format = aprs_pack.get('format', '')

        raw = aprs_pack.get('raw', '')
        if self._is_duplicate(raw):
            return False
        # 1. Nur Messages und Positions sind sinnvoll für IS→RF
        if packet_format not in ['message', 'position', 'object', 'item', 'wx']:
            return False

        # 2. Keine Pakete, die schon über RF kamen oder NOGATE/RFONLY haben
        via  = aprs_pack.get('via', '') or ''
        path = aprs_pack.get('path', [])
        if any(x.upper() in [p.upper() for p in path] for x in ['NOGATE', 'RFONLY']):
            return False
        if ',qAX,' in via or 'TCPXX' in via.upper():   # ungültiger Login auf IS
            return False

        # 3. Bei Messages: Zielstation muss kürzlich lokal gehört worden sein
        if packet_format == 'message':
            to_call = aprs_pack.get('address', '') or aprs_pack.get('addresse', '') or aprs_pack.get('to', '')
            if not to_call:
                return False

            # Schau in node_tab, ob wir die Station kürzlich gehört haben
            node_tab = self._get_node_tab()
            node = node_tab.get(to_call.upper(), {})
            if not node:
                return False

            rx_time = node.get('rx_time')
            if not rx_time:
                return False

            age_minutes = (datetime.now() - rx_time).total_seconds() / 60
            if age_minutes > self._igate_local_time:
                return False

            # Optional: Entfernung prüfen
            dist = node.get('distance', -1)
            if dist > 0 and dist > self._igate_max_distance:
                return False

            return True

        # 4. Bei Positions/Objects/WX: nur wenn Station kürzlich gehört wurde (oder eigene Config-Regel)
        # Hier kannst du später erweitern (z.B. nur innerhalb 50 km)
        node_tab = self._get_node_tab()
        node = node_tab.get(aprs_pack.get('from', '').upper(), {})
        if node:
            age_minutes = (datetime.now() - node.get('rx_time', datetime.now())).total_seconds() / 60
            if age_minutes < self._igate_local_time * 2:   # etwas großzügiger für Positions
                dist = node.get('distance', -1)
                if dist <= self._igate_max_distance or dist < 0:
                    return True

        return False

    def _is_duplicate(self, raw):
        now = time.time()
        if raw in self._dupe_cache:
            if now - self._dupe_cache[raw] < self._igate_dup_time:
                return True
        self._dupe_cache[raw] = now
        return False

    def _allow_tx(self):
        now = time.time()
        self._tx_counter = [t for t in self._tx_counter if now - t < 60]

        if len(self._tx_counter) > APRS_IGATE_RATE_LIMIT:
            return False

        self._tx_counter.append(now)
        return True

    @staticmethod
    def _unwrap_thirdparty(aprs_pack: dict):
        """Extrahiert ein Third-Party Paket und macht ein normales APRS-Pack daraus"""
        if aprs_pack.get('format') != 'thirdparty':
            return aprs_pack

        sub = aprs_pack.get('subpacket', {})
        if not sub:
            return None

        # Original RF Path behalten!
        path     = aprs_pack.get('path', [])

        new_pack = dict(sub)

        # WICHTIG: Path vom äußeren Paket übernehmen
        new_pack['path']            = path
        new_pack['via']             = aprs_pack.get('via', '')
        new_pack['port_id']         = aprs_pack.get('port_id')
        new_pack['rx_time']         = aprs_pack.get('rx_time')
        new_pack['was_thirdparty']  = True

        return new_pack

    def send_full_aprs_to_is(self, aprs_pack: dict):
        """Sendet RF-Paket als korrekten flachen TNC2-String an APRS-IS"""
        ais = self._aprs_ais.get_ais()
        if ais is None or not self._igate_active or not self._igate_call:
            if not self._igate_call:
                logger.error("APRS I-Gate: Kein igate_call (ais_call) gesetzt!")
            return

        try:
            # Thirdparty unwrap
            if aprs_pack.get('format') == 'thirdparty':
                aprs_pack = self._unwrap_thirdparty(aprs_pack)
                if not aprs_pack:
                    return

            # From / To
            from_call = aprs_pack.get('from', '').strip()
            to_call   = aprs_pack.get('to', 'APRS').strip()

            raw = aprs_pack.get('raw', '')

            if ':' in raw:
                info = raw.split(':', 1)[1]
            else:
                info = ''

            # Path sauber machen
            original_path = aprs_pack.get('path', [])
            clean_path = [p.strip() for p in original_path
                          if p.replace('*', '').strip().upper() not in
                          ('TCPIP', 'TCPXX', 'NOGATE', 'RFONLY', 'qAR', 'qAO', 'qAC')]

            # === WICHTIG: Voller TNC2-String ===
            # q_con = "qAR" if self._igate_is_to_rf else "qA????????"
            is_thirdparty = aprs_pack.get('was_thirdparty', False)
            q_flag = "qAO" if is_thirdparty else "qAR"
            if clean_path:
                path_str = ','.join(clean_path)
                packet_str = f"{from_call}>{to_call},{path_str},{q_flag},{self._igate_call}:{info}"
            else:
                packet_str = f"{from_call}>{to_call},{q_flag},{self._igate_call}:{info}"

            # Senden
            self._aprs_ais.ais_tx(packet_str)

            logger.info(f"IGate RF→IS: {from_call} via {clean_path or 'direct'} → IS")
            logger.debug(f"Sent to IS: {packet_str}")
            logger.debug(f"Sent to IS aprs-pack: {aprs_pack}")

        except Exception as e:
            logger.error(f"send_full_aprs_to_is Fehler: {e}", exc_info=True)


