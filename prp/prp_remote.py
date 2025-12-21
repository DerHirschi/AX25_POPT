"""
(P)oPT (R)emote (P)rotocol
"""
import hashlib
import os

from cfg.logger_config import logger
from fnc.ax25_fnc import reverse_uid
from prp.prp_auth_handler import PRPAuthHandler
from prp.prp_const import PRP_NACK, \
    PRP_OPT_21, PRP_OPT_DISCO, PRP_OPT_LOGIN_REQ, PRP_OPT_LOGIN_RESP, PRP_OPT_LOGOUT, PRP_OPT_STATE_UPDATE, \
    PRP_OPT_ESC_CLI, PRP_RM_RESP_LOGOUT, PRP_RM_RESP_LOGIN, \
    PRP_ACK
from prp.prp_handshake_handler import PRPHandshakeHandler
from prp.prp_protocol_handler import PRPProtocolHandler
from prp.prp_remote_monitor import PRPRemoteMonitor
from prp.prp_rx_processor import PRP_RX_Processor
from prp.prp_state_manager import PRPStateManager
from prp.prp_tx_buffer import PrpTxBuffer

DBUG_PW = 'test1234'


class PRPremote:
    def __init__(self, port_handler, connection):
        # == Port Handler
        self._port_handler = port_handler
        self._get_gui      = lambda : self._port_handler.get_gui()

        # == Connection
        self._connection   = connection
        if self._connection.is_incoming_conn:
            self._uid          = str(reverse_uid(connection.uid))
            self._remote_uid   = str(connection.uid)
        else:
            self._uid          = str(connection.uid)
            self._remote_uid   = str(reverse_uid(connection.uid))


        # ===================================================================
        # ======== Classes
        # == State Manager
        self._state_manager  = PRPStateManager(self)
        # == Handshake
        self._handshake      = PRPHandshakeHandler(self)
        # == Auth
        self._prp_auth       = PRPAuthHandler(self)
        # == TX Buffer
        self._tx_buffer      = PrpTxBuffer()
        # == RX Processor & Protocol
        self._rx_processor   = PRP_RX_Processor(self)
        self._protocol       = PRPProtocolHandler(self)
        # == Remote Monitor
        self._remote_monitor = PRPRemoteMonitor(self)

        #################################
        # Helper TX-Buffer
        self.is_tx_buffer             = lambda: self._tx_buffer.is_tx_buffer
        self.is_prp_opt_id_in_tx_buff = lambda opt_id: self._tx_buffer.is_prp_opt_id_in_tx_buff(opt_id)

        #################################
        # CLI ESC / Komprimiert senden
        # == Self / State I/O
        self._is_cli_esc_mode         = lambda: self._state_manager.own.get('cli_esc', False)

        #################################
        # Rechte System
        # std rechte aus popt_cfg
        # User rechte aus db

        #################################

    @property
    def uid(self):
        return self._uid

    @property
    def port_handler(self):
        return self._port_handler

    @property
    def connection(self):
        return self._connection

    @property
    def cli(self):
        if not hasattr(self._connection, 'cli'):
            return None
        return self._connection.cli

    # ==== PRP Classes
    @property
    def tx_buffer(self):
        return self._tx_buffer

    @property
    def rx_processor(self):
        return self._rx_processor

    @property
    def protocol(self):
        return self._protocol

    @property
    def remote_monitor(self):
        return self._remote_monitor

    @property
    def state_manager(self):
        return self._state_manager

    @property
    def handshake(self):
        return self._handshake

    @property
    def prp_auth(self):
        return self._prp_auth

    #####################################
    # Tasker (ax25Conn)
    def tasker(self):
        """ Called fm ax25Conn """
        self._remote_monitor.task()
        return True

    ###############################
    # PRP I/O - TX/RX
    def prp_tx(self, opt_id: int, tx_flag: bool, data: bytes,
               prio=False, compress=True, send_uncompressed=True):
        frame = self._protocol.encode_frame(opt_id, tx_flag, data, compress, send_uncompressed)
        if not frame:
            self._rx_processor.clear_last_pack_meta()
            return False

        abort = (opt_id == PRP_OPT_21 and not tx_flag)
        self._tx_buffer.write_to_buffer((opt_id, frame), prio=prio, is_abort_frame=abort)
        return True

    def prp_rx(self, data: bytes):
        """
        Eingehende Daten vom AX25-Layer.
        Leitet einfach an den RX-Processor weiter.
        """
        return self._rx_processor.process(data)

    # ====== Processing PRP-Frame
    def prp_rx_process(self, frame: bytes):
        """
        Wird vom RX_Processor aufgerufen, sobald ein vollständiges Frame extrahiert wurde.
        """
        try:
            return self._protocol.decode_and_dispatch(frame)
        except EncodingWarning:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in protocol handler: {e}")
            raise

    # ===================================================================
    # ====== PRP CLI-ESC I/O
    # ===================================================================
    def prp_tx_esc_cli(self, payload: bytes):
        """ Sende CLI Escape - AX25Conn.send_data() """
        # ESC-CLI Mode ist deaktiviert
        if not self._is_cli_esc_mode():
            return False

        # Wird nur gesendet, wenn es sich lohnt (Komprimierung)
        send_as_prp = self.prp_tx(
            opt_id=PRP_OPT_ESC_CLI,
            tx_flag=True,
            data=payload,
            prio=True,
            compress=True,
            send_uncompressed=False
        )
        # Wenn gesendet nicht gesendet, lösche Metadaten für Status MSG
        if not send_as_prp:
            self._rx_processor.clear_last_pack_meta()
        # Zurück zur AX25Conn.send_data()
        return send_as_prp

    def prp_rx_esc_cli(self, payload: bytes):
        self.send_cli_esc_recv_status()
        return payload

    #####################################
    # Remote Monitor Stream - OPT 0 - 19
    def remote_monitor_update(self, ax25frame_conf: dict):
        """ Called fm port_handler > connection.update_monitor() """
        if (not self._state_manager.get_own('cli_rem_mon') and
            not self._state_manager.get_own('gui_rem_mon')):
            return
        self._remote_monitor.update(ax25frame_conf)

    #####################################
    # Response Handler
    def local_response_handler(self, opt_id: int, resp_ok=True):
        """ Lokaler Response Handler / Bei erhalten eines RESP Paketes, nach ACK """
        uid = self._uid

        # ==== Opt bezogener RESP
        # == Handshake
        #if opt_id == PRP_OPT_20:
        #    # if resp_ok:
        #    self._gui_resp_handshake()  # Jetzt erst nach ACK

        # == Login
        if opt_id == PRP_OPT_LOGIN_RESP:
            if resp_ok:
                self._port_handler.handle_prp_response(PRP_RM_RESP_LOGIN, uid)
                return
            self._port_handler.handle_prp_response(PRP_RM_RESP_LOGOUT, uid)
            return

        # == Logout
        elif opt_id == PRP_OPT_LOGOUT:
            self._port_handler.handle_prp_response(PRP_RM_RESP_LOGOUT, uid)
            return
        #################################
        # Globaler RESP für Remote Monitor
        self._port_handler.handle_prp_response('', uid)

    #####################################
    # CTL CMD's - OPT 20 - 63
    # ...................................
    # == OPT-ID 20 - Handshake
    def init_prp_handshake(self, remote_identy):
        """ Bekommt Station Identy Objekt von CLI """
        self._handshake.init_from_cli(remote_identy)

    @property
    def is_handshake(self):
        return self._handshake.is_completed

    @property
    def is_handshake_pending(self):
        return self._handshake.is_pending

    def _gui_resp_handshake(self):
        # == GUI Response
        gui = self._get_gui()
        if not hasattr(gui, 'init_popt_remote'):
            return
        #
        gui.init_popt_remote(self._uid)
        #gui.init_popt_remote(self._remote_uid)

    # =============================
    # ====== OPT-ID 21 - Abort
    # == CLI Abort
    def cli_abort(self):
        if not self.is_handshake:
            return False

        # == Prüfe ob CLI-ESC Pakte im TX-Buffer sind
        if not self._tx_buffer.is_prp_opt_id_in_tx_buff(PRP_OPT_ESC_CLI):
            return False
        # == Sende ABORT-RESP Frame
        self._protocol.send_abort_request()
        return True

    # =============================
    # ====== OPT-ID 22 - Disconnect CMD
    def cmd_disco(self):
        """ TX Start Disco CMD """
        if not self.is_handshake:
            return
        self.prp_tx(opt_id=PRP_OPT_DISCO, tx_flag=True, data=b'', prio=True)

    def rx_cmd_disco(self):
        """ RX Start Disco CMD """
        # == Remote Monitor abschalten
        self._state_manager.set_own('gui_rem_mon', False)
        self._state_manager.set_own('cli_rem_mon', False)
        # == TX-Buffer löschen
        self._tx_buffer.del_tx_buff(None)
        # == Connection Disco
        self._connection.conn_disco()

    # =============================
    # ====== OPT-ID 23/24 -Login Stuff
    def cmd_login_request(self, password: str):
        """Client fordert Login-Challenge an"""
        if not self.is_handshake:
            logger.warning("PRP Auth: Login-Request ohne Handshake")
            return
        self._prp_auth.request_login(DBUG_PW)

    # =============================
    # ====== OPT-ID 25 - Logout Stuff
    def cmd_logout(self):
        """ Client sendet Logout """
        if not self.is_handshake:
            return
        self._prp_auth.initiate_logout()

    # =============================
    # ==== OPT-ID 26 - States Update via Remote / By Grok AI
    def send_remote_state_update(self, state_updates: dict):
        # send_remote_state_update({'batch_mode': 'off', 'cli_esc': True})
        if not self.is_handshake:
            return False

        # update abgleichen mit _remote_states was sich geändert hat
        update_to_send = {}
        for k, v in state_updates.items():
            if self._state_manager.get_remote(k) != v:
                update_to_send[k] = v
        # Keine Updates?
        if not update_to_send:
            return False

        # Logger
        logger.debug(f"PRP: Sende State Update: {self._uid}")
        for k, v in update_to_send.items():
            logger.debug(f"PRP: {k}:{v}")

        # Pending für ACK
        self._state_manager.add_pending(PRP_OPT_STATE_UPDATE, update_to_send)

        bin_payload = self._state_manager.encode_updates(update_to_send)
        if not bin_payload:
            return False

        return self.prp_tx(
            opt_id=PRP_OPT_STATE_UPDATE,
            tx_flag=True,
            data=bin_payload,
            prio=True,
            compress=True
        )

    # ==== Public State I/O API
    # == Own States
    @property
    def get_own_states(self):
        return dict(self._state_manager.own)

    def set_own_state(self, state_key: str, value):
        return self._state_manager.set_own(state_key, value)

    def update_own_states(self, state_cfg: dict):
        """
        Validator für GUI Parameter
        by Grok-AI
        Updated mehrere _own_states auf einmal aus einem Dict.
        Validiert jeden Eintrag (Key, Typ, Wert) vor dem Setzen.
        Bei einem einzigen Fehler wird KEINE Änderung vorgenommen.

        Beispiel:
            self.update_own_states({
                'gui_rem_mon': True,
                'rem_mon_port': 5,
                'batch_mode': 'off',
                'rem_mon_incl': ['DB0LJ', 'DL1ABC']
            })

        Rückgabe: True = alles erfolgreich gesetzt, False = mind. ein Fehler
        """
        return self._state_manager.update_own(state_cfg)

    # == Remote States
    @property
    def get_rem_states(self):
        return dict(self._state_manager.remote)

    def get_rem_state_by_key(self, state_key: str):
        if not state_key in self._state_manager.remote:
            return None
        return self._state_manager.get_remote(state_key)

    #####################################
    # CLI I/O
    # ==== QSO Stream I/O
    def _send_cli_esc_status_to_QSO(self, status_msg: str, tx: bool):
        if not hasattr(self._connection, 'send_gui_QSO_PRPstatus'):
            return
        self._connection.send_gui_QSO_PRPstatus(status_msg, tx=tx)

    # === CLI-ESC Status Meldungen für gui.QSO
    def get_cli_esc_sender_status(self):
        """
        TX.
        Gibt den Status eines gesendeten CLI-ESC-Frames zurück, falls vorhanden.
        """
        if self._rx_processor.last_pack_meta is None:
            return None

        len_payload, len_compressed = self._rx_processor.last_pack_meta
        compression_ratio = round((len_payload / len_compressed) * 100)

        return f"PRP ▲ Compressed({compression_ratio}%) - {len_compressed}/{len_payload} Bytes"

    def send_cli_esc_recv_status(self):
        """
        RX.
        Gibt den Status eines unvollständigen CLI-ESC-Frames zurück, falls vorhanden.
        """
        if self._rx_processor.next_pack_meta is None and self._rx_processor.comp_pack_meta is None:
            return  # Kein unvollständiges Frame oder Header unvollständig

        # == Paket ist noch im Empfang (Restbuffer)
        if self._rx_processor.next_pack_meta is not None:
            opt_id, payload_len = self._rx_processor.next_pack_meta
            # == Nur für CLI-ESC (OPT 62, TX-Flag)
            if opt_id != PRP_OPT_ESC_CLI:
                return

            # == Berechne Fortschritt
            total_bytes = 7 + payload_len  # Flag(2) + OPT(1) + LEN(2) + Payload + CRC(2)
            received_bytes = self._rx_processor.rest_buffer_len

            if not received_bytes:
                return

            # === Noch nicht vollständig → Fortschritt anzeigen ===
            if received_bytes < total_bytes:
                percent = int((received_bytes / total_bytes) * 100)
                pr_ten = round(percent / 10)
                pr_rest = 10 - pr_ten
                ## Download Bar
                bar = f"{'#' * pr_ten}{'.' * pr_rest}"
                status_msg = f"PRP ▼ [{bar}]({str(percent).ljust(3)}%) - {received_bytes - 7}/{payload_len} Bytes"
                self._send_cli_esc_status_to_QSO(status_msg, tx=False)
                return


        # === Genau 100 % → Erfolgsmeldung (einmalig anzeigen) ===
        if self._rx_processor.comp_pack_meta is not None:
            opt_id, prp_payload_len, payload_len = self._rx_processor.comp_pack_meta
            if opt_id != PRP_OPT_ESC_CLI:
                return
            # Optional: Kompressionsrate berechnen (wenn möglich)
            try:
                comp_ratio = f"{round(payload_len / prp_payload_len * 100)}"
            except Exception as ex:
                null = ex
                comp_ratio = "?"
            bar = '#' * 10
            status_msg = f"PRP ▼ [{bar}](100%) - Compressed({comp_ratio}%) - Data:{prp_payload_len}/{payload_len} Bytes"
            self._send_cli_esc_status_to_QSO(status_msg, tx=False)

            self._rx_processor.clear_comp_pack_meta()
            return

        # === Mehr als total_bytes → sollte nie passieren, aber sicherheitshalber ===
        return

    # == CLI-ESC ABORT Meldungen für gui.QSO
    def send_cli_esc_abort_sender_status(self):
        """
        TX.
        Sendet ABORT Mitteilung an gui.qso
        """
        status_msg = f"\nPRP ■ !ABORT!"
        self._send_cli_esc_status_to_QSO(status_msg, tx=True)

    def send_cli_esc_abort_recv_status(self):
        """
        RX.
        Sendet ABORT Mitteilung an gui.qso
        """
        if self._rx_processor.next_pack_meta is None:
            return

        opt_id, payload_len = self._rx_processor.next_pack_meta
        # == Nur für CLI-ESC (OPT 62, TX-Flag)
        if opt_id != PRP_OPT_ESC_CLI:
            logger.info(f"PRP: Abgebrochener Frame OPT-ID: {opt_id} - UID: {self._uid}")
            return

        # === Fortschritt anzeigen ===
        status_msg = f"PRP ■ [{'-' * 10}](0  %) ABORT/{payload_len} Bytes"
        self._send_cli_esc_status_to_QSO(status_msg, tx=False)
        return



