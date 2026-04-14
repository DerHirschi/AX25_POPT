import time
from collections import deque
from datetime import datetime

from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG


class APRSDigiPeater:
    def __init__(self):
        logger.info("APRS-DIGI: Init")

        self._dupe_cache    = {}
        self._dupe_time     = 30
        # ====================
        # CFG
        ais_cfg             = POPT_CFG.get_CFG_aprs_ais()
        self._mycall        = ais_cfg.get('ais_call', '').upper()

        # Betriebsmodi
        digi_cfg            = POPT_CFG.get_CFG_aprs_digi()
        self._enabled       = digi_cfg.get('digi_active',       True)
        self._is_fillin     = digi_cfg.get('digi_fillin',       True)   # Fill-In Digi (WIDE1-1 only)
        self._trace_enabled = digi_cfg.get('digi_trace_active', True)
        self._trace_all     = digi_cfg.get('digi_trace_all',    True)
        self._dupe_time     = digi_cfg.get('digi_dup_time',     30)
        self._digi_ports    = digi_cfg.get('digi_ports',        [])

        # === Verlauf/Monitor
        self._monitor_buffer = deque([], maxlen=10000)

        # === Config Check
        if not self._mycall:
            logger.info("APRS-DIGI: No APRS Station (Call) configured yet. APRS-DIGI disabled!")
            self._enabled = False

    ############################################################
    def handle_rx(self, aprs_pack: dict):
        if not self._enabled:
            return None

        if not aprs_pack:
            return None

        port_id = aprs_pack.get('port_id', '')
        if str(port_id) not in map(str, self._digi_ports):
            return None

        # 8. Eigene Calls
        from_call = aprs_pack.get('from', '').upper()
        to_call   = aprs_pack.get('addresse', '').upper()
        if (to_call in POPT_CFG.get_stat_CFG_keys() or
                from_call in POPT_CFG.get_stat_CFG_keys()):
            logger.info("APRS-DIGI: To/From Call is own Station. No Digipeating...")
            return None

        path = aprs_pack.get('path', [])
        if not path:
            return None

        self._cleanup_dupes()
        raw = aprs_pack.get('raw', '')
        if self._is_duplicate(raw):
            return None

        # Loop Protection (mein Call schon im Path?)
        if self._has_mycall(path):
            return None

        new_path = self._process_path(aprs_pack)

        if not new_path:
            return None

        new_pack                     = dict(aprs_pack)
        new_pack['path']             = new_path
        raw                          = aprs_pack.get('raw', '')
        if ':' in raw:
            new_pack['raw_message_text']  = raw.split(':', 1)[1]
            aprs_pack['raw_message_text'] = raw.split(':', 1)[1]
        else:
            new_pack['raw_message_text']  = ''
            aprs_pack['raw_message_text'] = ''

        logger.debug(f"APRS-DIGI ({self._mycall}): {aprs_pack.get('from')} → {new_path}")
        logger.debug(f"APRS-DIGI ({self._mycall}): APRS-Pack → {aprs_pack}")
        logger.debug(f"APRS-DIGI ({self._mycall}): New-Pack → {new_pack}")
        # ==== DIGI Monitor
        new_pack['tx_time'] = datetime.now()
        new_pack['dir']     = 'out'
        new_pack['txport']  = port_id
        aprs_pack['dir']    = 'in'
        self._monitor_buffer.append(aprs_pack)
        self._monitor_buffer.append(new_pack)

        return new_pack

    ############################################################
    def _process_path(self, aprs_pack):
        path = aprs_pack.get('path', [])
        new_path = []

        for i, p in enumerate(path):
            call = p.upper()

            # Bereits benutzt
            if call.endswith('*'):
                new_path.append(call)
                continue

            base, n = self._parse_path(call)

            # ==================================================
            # WIDE1-1 (Fill-In)
            # ==================================================
            if base == "WIDE1" and n == 1:
                if self._is_fillin and self._is_direct(aprs_pack):
                    new_path.append(f"{self._mycall}*")
                    return new_path + path[i + 1:]
                else:
                    new_path.append(call)
                    continue

            # ==================================================
            # WIDEn-N
            # ==================================================
            if base.startswith("WIDE") and n is not None:
                if self._is_fillin and not self._trace_all:
                    # Fill-In darf kein WIDE2+
                    if base != "WIDE1":
                        return None
                if n <= 0:
                    return None

                new_path.append(f"{self._mycall}*")
                if n > 1:
                    new_path.append(f"{base}-{n - 1}")

                return new_path + path[i + 1:]

            # ==================================================
            # TRACE
            # ==================================================
            if base.startswith("TRACE") and self._trace_enabled:
                if n <= 0:
                    return None

                new_path.append(f"{self._mycall}*")
                if n > 1:
                    new_path.append(f"{base}-{n - 1}")

                return new_path + path[i + 1:]

            # normal übernehmen
            new_path.append(call)

        return None

    @staticmethod
    def _parse_path(call):
        try:
            if '-' in call:
                base, ssid = call.split('-')
                return base, int(ssid)
            return call, None
        except Exception as ex:
            logger.error(ex)
            return call, None

    ############################################################
    @staticmethod
    def _is_direct(aprs_pack):
        """
        Direkt empfangen = kein '*' im Path
        """
        path = aprs_pack.get('path', [])
        return not any('*' in p for p in path)

    def _has_mycall(self, path):
        for p in path:
            clean = p.replace('*', '')
            if clean == self._mycall:
                return True
        return False
    ############################################################
    def _is_duplicate(self, raw):
        now = time.time()

        if raw in self._dupe_cache:
            if now - self._dupe_cache[raw] < self._dupe_time:
                return True

        self._dupe_cache[raw] = now
        return False

    def _cleanup_dupes(self):
        now = time.time()
        self._dupe_cache = {
            k: t for k, t in self._dupe_cache.items()
            if now - t < self._dupe_time
        }

    ############################################################
    def get_digi_mon_buf(self):
        return self._monitor_buffer

