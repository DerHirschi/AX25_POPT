import datetime
import time

from cfg.logger_config import logger
from classes.CLbuffers import ListBuffer
from fnc.ax25_fnc import reverse_uid
from prp.prp_const import PRP_BATCH_MIN_PACK
from prp.prp_dec_fnc import pack_time_hms


class PRPRemoteMonitor:
    """
    Verantwortlich für:
    - Remote Monitor Stream (OPT-ID 0–19)
    - Batch-Modus (Sammeln und komprimiertes Senden)
    - Filterung (Port, Include/Exclude, eigene Frames)
    - ABORT bei Remote-Monitor-Aus
    """

    def __init__(self, prp_root):
        """
        :param prp_root: Referenz auf PRPremote-Instanz
        """
        self._prp_root          = prp_root
        self._state_manager     = prp_root.prp_state_manager
        self._prp_tx_buffer     = prp_root.prp_tx_buffer
        self._prp_protocol      = prp_root.prp_protocol
        self._prp_control       = prp_root.prp_control

        # == UID
        self._uid               = self._prp_root.uid
        self._reverse_uid       = reverse_uid(self._uid)

        # == Batch-Buffer und Timer
        self._batch_buffer = ListBuffer()  # Speichert ax25frame_conf Dict
        self._batch_timer  = time.time() + self._state_manager.get_own('batch_wait')

    def _get_batch_wait(self):
        return self._state_manager.get_own('batch_wait')

    def _is_gui_rem_mon(self):
        return self._state_manager.get_own('gui_rem_mon')

    def _is_cli_rem_mon(self):
        return self._state_manager.get_own('cli_rem_mon')

    def _get_rem_mon_port(self):
        return self._state_manager.get_own('rem_mon_port')

    def _get_incl_filter(self):
        return self._state_manager.get_own('rem_mon_incl')

    def _get_excl_filter(self):
        return self._state_manager.get_own('rem_mon_excl')

    def _is_batch_mode(self):
        return self._state_manager.get_own('batch_mode') == 'on'

    def _is_batch_mode_auto(self):
        return self._state_manager.get_own('batch_mode') == 'auto'

    def _can_send_next_batch(self, payload_len: int):
        return self._prp_tx_buffer.can_send_next_prp_batch(payload_len)


    # ===================================================================
    # Eingehender Monitor-Frame (vom lokalen PortHandler)
    # ===================================================================
    def update(self, ax25frame_conf: dict):
        """
        Wird von PortHandler → Connection.update_monitor() aufgerufen.
        Prüft Filter und entscheidet, ob Frame remote gesendet werden soll.
        """
        if self._prp_root.connection is None:
            # TODO Für eigene L3 Verbindung verfügbar machen
            return

        port_id = ax25frame_conf.get('port', -1)
        if port_id != self._get_rem_mon_port():
            return

        from_call = ax25frame_conf.get('from_call_str', '')
        to_call = ax25frame_conf.get('to_call_str', '')
        frame_uid = ax25frame_conf.get('uid', '')
        my_uid     = self._uid
        my_uid_rev = self._reverse_uid

        # Eigene Verbindung filtern
        if frame_uid in (my_uid, my_uid_rev):
            return
        if (to_call == self._prp_root.connection.to_call_str_add and
            from_call == self._prp_root.connection.my_call_str_add) or \
                (from_call == self._prp_root.connection.to_call_str_add and
                 to_call == self._prp_root.connection.my_call_str_add):
            return

        # Exclude-Filter
        excl = self._get_excl_filter()
        if excl and (from_call in excl or to_call in excl):
            return

        # Include-Filter
        incl = self._get_incl_filter()
        if incl and not (from_call in incl or to_call in incl):
            return

        # CLI-Monitor (falls aktiviert)
        #if self._is_cli_rem_mon():
        #    self._prp_root.connection.cli.cli_update_monitor(ax25frame_conf)

        # Batch-Entscheidung
        payload_len = self._prp_root.connection.get_PacLen * self._prp_root.connection.get_MaxPac

        if (self._is_batch_mode() or
                not self._batch_buffer.is_empty or
                (self._is_batch_mode_auto() and not self._can_send_next_batch(payload_len))):
            self._batch_buffer.buffer_write(ax25frame_conf)
            return

        # Direkt senden (nur GUI aktiv)
        if self._is_gui_rem_mon():
            self.send_single_frame(ax25frame_conf)

    # ===================================================================
    # Senden
    # ===================================================================
    def send_single_frame(self, ax25frame_conf: dict):
        """Sendet ein einzelnes Monitor-Frame (nicht gebatched)"""
        ax25_raw = ax25frame_conf.get('ax25_raw', b'')
        tx = ax25frame_conf.get('tx', False)
        port_id = ax25frame_conf.get('port', 0)
        rx_time = ax25frame_conf.get('rx_time', datetime.datetime.now())

        data = pack_time_hms(rx_time) + ax25_raw
        self._prp_root.prp_tx(opt_id=int(port_id), tx_flag=tx, data=data, prio=False)

    def _build_batch_frames(self):
        """Erstellt eine Liste von encoded PRP-Frames aus dem Batch-Buffer"""
        batch_frames = []
        while self._batch_buffer.length:
            conf = self._batch_buffer.buffer_read
            ax25_raw = conf.get('ax25_raw', b'')
            tx = conf.get('tx', False)
            port_id = conf.get('port', 0)
            rx_time = conf.get('rx_time', datetime.datetime.now())

            data = pack_time_hms(rx_time) + ax25_raw
            encoded = self._prp_protocol.encode_frame(
                opt_id=int(port_id),
                tx=tx,
                data=data,
                compress=False  # Monitor-Frames einzeln nicht komprimieren
            )
            if encoded:
                batch_frames.append(encoded)
        return batch_frames

    def send_batch(self):
        """Sendet den gesammelten Batch (wird vom Tasker aufgerufen)"""
        if self._batch_buffer.is_empty:
            self._batch_timer = time.time() + self._get_batch_wait()
            return

        # Buffer- oder Zeitlimit erreicht?
        buffer_limit = self._batch_buffer.length > 30
        if self._batch_timer > time.time() and not buffer_limit:
            return

        if self._prp_root.connection is None:
            payload_len = 750 # TODO payload_len für PRP-L3
        else:
            payload_len = self._prp_root.connection.get_PacLen * self._prp_root.connection.get_MaxPac
        if not self._can_send_next_batch(payload_len) and not buffer_limit:
            return

        # Timer resetten
        self._batch_timer = time.time() + self._get_batch_wait()

        batch_len = self._batch_buffer.length
        send_as_batch = batch_len > PRP_BATCH_MIN_PACK

        if not send_as_batch:
            # Zu klein → einzeln senden
            while self._batch_buffer.length:
                conf = self._batch_buffer.buffer_read
                self.send_single_frame(conf)
            return

        # Als echter Batch senden
        batch_frames = self._build_batch_frames()
        if batch_frames:
            self._prp_protocol.prp_batch_tx(batch_frames)

        # Buffer leeren (falls nicht bereits durch _build_batch_frames geschehen)
        self._batch_buffer.buffer_clear()

    # ===================================================================
    # Tasker & Abort
    # ===================================================================
    def task(self):
        """Wird vom PRPremote.tasker() aufgerufen"""
        self.send_batch()

    def abort(self):
        """Wird aufgerufen, wenn Remote-Monitor ausgeschaltet wird"""
        logger.debug(f"PRP: Remote Monitor Abort für UID {self._prp_root.uid}")
        self._batch_buffer.buffer_clear()

        self._prp_control.handle_remote_mon_abort()  # Abort-Frame senden

