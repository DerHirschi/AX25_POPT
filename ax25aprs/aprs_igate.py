from cfg.popt_config import POPT_CFG
from cfg.logger_config import logger
from datetime import datetime


class APRSiGate:
    def __init__(self, aprs_ais, port_handler):
        self._aprs_ais     = aprs_ais
        self._ais          = aprs_ais.get_ais()
        self._port_handler = port_handler

        # ====================
        # CFG
        ais_cfg = POPT_CFG.get_CFG_aprs_igate()

        self._igate_active       = ais_cfg.get('igate_active',       True)  # Globaler Schalter
        self._igate_rf_to_is     = ais_cfg.get('igate_rf_to_is',     True)   # RF → IS (meist immer an)
        self._igate_is_to_rf     = ais_cfg.get('igate_is_to_rf',     True)  # IS → RF (vorsichtig!)
        self._igate_max_distance = ais_cfg.get('igate_max_distance', 80)     # km für IS→RF
        self._igate_local_time   = ais_cfg.get('igate_local_time',   45)     # Minuten, wie lange eine Station "lokal" gilt
        self._igate_ports        = ais_cfg.get('igate_ports',        [])     # Liste von Port-IDs, auf denen I-Gate aktiv sein soll (leer = alle)
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


    ##########################
    # I-Gate Helper
    def should_gate_to_is(self, aprs_pack: dict, port_id: str):
        """Entscheidet, ob ein RF-Paket ins APRS-IS (Internet) weitergeleitet werden soll."""
        if not (self._igate_active and self._igate_rf_to_is):
            return False

        # Nur auf erlaubten Ports (falls eingeschränkt)
        if self._igate_ports and str(port_id) not in map(str, self._igate_ports):
            return False

        packet_format = aprs_pack.get('format', '')
        via = aprs_pack.get('via', '') or ''
        path = aprs_pack.get('path', [])

        # 1. Keine Pakete, die schon aus dem Internet kommen
        if any(x in via.upper() for x in ['TCPIP', 'TCPXX']):
            return False
        if any(x.upper() in [p.upper() for p in path] for x in ['TCPIP', 'TCPXX', 'NOGATE', 'RFONLY']):
            return False

        # 2. Keine Generic Queries (?)
        if packet_format == 'query' or aprs_pack.get('raw_message_text', '').startswith('?'):
            return False

        # 3. Keine 3rd-Party-Pakete mit Internet-Spuren (optional: ganz ablehnen oder bereinigen)
        if packet_format == 'thirdparty':
            sub = aprs_pack.get('subpacket', {})
            if any(x in str(sub.get('path', '')) for x in ['TCPIP', 'TCPXX']):
                return False

        # 4. Keine ungültigen Calls (optional, aber sinnvoll)
        from_call = aprs_pack.get('from', '').upper()
        if from_call.startswith(('WIDE', 'RELAY', 'TRACE', 'NOCALL', 'N0CALL')):
            return False

        # Alles andere → ja (Standard für RF→IS)
        return True


    def should_gate_to_rf(self, aprs_pack: dict):
        """Entscheidet, ob ein Paket vom APRS-IS auf RF gesendet werden soll.
           Sehr restriktiv! Standard ist nur Messages + Positions von lokalen Stationen."""
        if not (self._igate_active and self._igate_is_to_rf):
            return False

        packet_format = aprs_pack.get('format', '')

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
            to_call = aprs_pack.get('addresse', '') or aprs_pack.get('to', '')
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


    def send_full_aprs_to_is(self, aprs_pack: dict):
        """Sendet ein vollständiges APRS-Paket (aus RF) an APRS-IS."""
        if self._ais is None or not self._igate_active:
            return

        try:
            # Baue den klassischen TNC2-String für APRS-IS
            from_call = aprs_pack.get('from', '')
            to_call   = aprs_pack.get('to', 'APRS')
            path      = aprs_pack.get('path', [])
            info      = aprs_pack.get('raw_message_text', '') or aprs_pack.get('info', '')

            # Path bereinigen und TCPIP* anhängen
            clean_path = [p.replace('*', '') for p in path if p.upper() not in ['TCPIP', 'TCPXX']]
            path_str = ','.join(clean_path) if clean_path else ''

            if path_str:
                packet_str = f"{from_call}>{to_call},{path_str},TCPIP*:{info}"
            else:
                packet_str = f"{from_call}>{to_call},TCPIP*:{info}"

            self._ais.ais_tx(packet_str)
            logger.debug(f"IGate RF→IS: {from_call} → IS")

        except Exception as e:
            logger.error(f"_send_full_aprs_to_is Fehler: {e}")


