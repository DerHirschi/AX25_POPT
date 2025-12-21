"""
(P)oPT (R)emote (P)rotocol
"""
import hashlib
import os

from cfg.logger_config import logger
from cli.cliStationIdent import get_station_id_obj
from fnc.ax25_fnc import reverse_uid
from fnc.str_fnc import version_tuple
from prp.prp_const import PRP_NACK, \
    PRP_OPT_20, PRP_OPT_21, PRP_OPT_DISCO, PRP_OPT_LOGIN_REQ, PRP_OPT_LOGIN_RESP, PRP_OPT_LOGOUT, PRP_OPT_STATE_UPDATE, \
    PRP_OPT_ESC_CLI, PRP_RM_RESP_LOGOUT, PRP_RM_RESP_LOGIN, \
    PRP_ACK, PRP_VER_RESTR, PRP_SW_RESTR, PRP_VER_RESTR_HANDSHAKE
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

        #################################
        # Helper PRP
        self._is_ack    = lambda payload: True if payload == PRP_ACK else False


        # ===================================================================
        # ======== Classes
        # == State Manager
        self._state_manager  = PRPStateManager(self)
        # == Handshake
        self._handshake      = PRPHandshakeHandler(self)
        # == TX Buffer
        self._tx_buffer      = PrpTxBuffer()
        # == RX Processor & Protocol
        self._rx_processor   = PRP_RX_Processor(self)
        self._protocol       = PRPProtocolHandler(self)



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
        # Login / AUTH
        # TODO Sysop Passwörter aus extra cfg Datei holen
        self._login_nonce    = None
        self._password_hash  = None  # sha256(password)
        # == Self / State I/O
        self._is_auth        = lambda        : self._state_manager.get_own('login_ok')
        self._set_auth       = lambda is_auth: self._state_manager.set_own('login_ok', is_auth)
        # == Remote / State I/O
        self._is_remote_auth = lambda        : self._state_manager.get_remote('login_ok')
        self._set_remote_auth= lambda is_auth: self._state_manager.set_remote('login_ok', is_auth)

        #################################
        # Remote Monitor
        self._remote_monitor = PRPRemoteMonitor(self)


    @property
    def uid(self):
        return self._uid

    @property
    def port_handler(self):
        return self._port_handler

    @property
    def connection(self):
        return self._connection

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
        self._send_cli_esc_recv_status()
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
    def _local_response_handler(self, opt_id: int, resp_ok=True):
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

    # == Response nach, erhalten eines Updates
    def _response_state_update(self, state_update: dict):
        """ Checke State-updates auf Änderungen und führe Action aus """
        # == Remote Monitor
        if self._state_manager.has_changed(state_update, 'gui_rem_mon'):
            # == Remote Monitor STOP
            if not state_update['gui_rem_mon']:
                # == Lösche TX-Buffer & sende ABORT-Resp
                self._remote_monitor.abort()
                return
        # == CLI-ESC Sync
        if self._state_manager.has_changed(state_update, 'cli_esc'):
            # == Sync CLI-ESC Own State with remote State
            self._state_manager.set_remote('cli_esc', state_update['cli_esc'])

    #####################################
    # CTL CMD's - OPT 20 - 63
    # ...................................
    # =============================
    # ====== OPT-ID 21 - ABORT

    def send_cmd_21(self):
        # TX CMD 21 - CLI-ESC ABORT
        if not self.is_handshake:
            return


        # == PRP ABORT-FRAME Senden
        self.prp_tx(opt_id=PRP_OPT_21, tx_flag=True, data=b'', prio=True)


    def _rx_cmd_21(self):
        """ RX CMD 21 - ABORT - CLI-ESC Abort """
        logger.info(
            f"PRP: Abort-REQ(CLI-ESC) empfangen (OPT-ID 21). Breche das Senden ab und lösche TX-Buffer. UID: {self._uid}")
        # == Status MSG to GUI ????????
        self._send_cli_esc_abort_sender_status()
        # == ESC-CLI Frame aus ax25Conn PRP-Rest-buffer löschen
        logger.debug(f"PRP: Lösche TX-Buffer (aktuellen Frame)und sende Abort RESP Frame: {self._uid}")
        # == Lösche AX25Conn sende Buffer (nut tx-buffer, nicht prp-q buffer)
        self._tx_buffer.del_tx_buff(PRP_OPT_ESC_CLI) # FIXME. Delete CLI-ESC Frames in prp-Q as well
        # == Send Response
        self._tx_resp_cmd_21()
        return

    def _tx_resp_cmd_21(self):
        """ TX Respond CMD 21 - ABORT RESP - Wird in unvollständig empfangenen PRP-Frame gesucht """
        # == Sende Abort Frame
        self.prp_tx(opt_id=PRP_OPT_21, tx_flag=False, data=b'', prio=True)


    def _rx_resp_cmd_21(self):
        """ RX Respond CMD 21 """
        logger.info(
            f"PRP: Abort-Frame empfangen (OPT-ID 21). Breche Empfang ab und lösche Rest-Buffer. UID: {self._uid}")

    # =============================
    # ====== OPT-ID 22 - Disconnect CMD
    def cmd_disco(self):
        """ TX Start Disco CMD """
        if not self.is_handshake:
            return
        self.prp_tx(opt_id=PRP_OPT_DISCO, tx_flag=True, data=b'', prio=True)

    def _rx_cmd_disco(self):
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
            return
        # TODO Password fm DB or GUI
        self._password_hash = hashlib.sha256(DBUG_PW.encode()).digest()
        self._state_manager.add_pending(PRP_OPT_LOGIN_RESP, {'login_ok': True})
        self.prp_tx(PRP_OPT_LOGIN_REQ, tx_flag=True, data=b'', prio=True)

    def _rx_cmd_login_request(self):
        """Client fordert Login-Challenge an"""
        nonce = os.urandom(16)
        self._login_nonce = nonce
        self.prp_tx(PRP_OPT_LOGIN_REQ, tx_flag=False, data=nonce, prio=True)

    def _rx_cmd_login_challenge(self, payload):
        """Client erhält Nonce vom Server"""
        self._login_nonce = payload
        print("LOGIN Challenge erhalten.")
        self._cmd_login_send_response()

    def _cmd_login_send_response(self):
        if not self._login_nonce:
            print("Keine Challenge empfangen!")
            return

        h = hashlib.sha256(self._password_hash + self._login_nonce).digest()
        self.prp_tx(PRP_OPT_LOGIN_RESP, tx_flag=True, data=h, prio=True)

    def _rx_cmd_login_response(self, payload):
        """Server prüft kryptografische Antwort"""
        # TODO password_hash fm userdb
        password      = DBUG_PW
        password_hash = hashlib.sha256(password.encode()).digest()

        if not self._login_nonce or not password_hash:
            self._send_login_ack(False)
            logger.error(f"PRP: Remote Login error !! UID: {self._uid}")
            return

        expected = hashlib.sha256(password_hash + self._login_nonce).digest()

        if expected == payload:
            logger.info(f"PRP: Remote Login accepted !! UID: {self._uid}")
            self._set_auth(True)
            self._send_login_ack(True)
        else:
            logger.warning(f"PRP: Remote Login failed !! UID: {self._uid}")
            self._set_auth(False)
            self._send_login_ack(False)

        self._login_nonce   = None
        self._password_hash = None

    def _send_login_ack(self, ok: bool):
        data = PRP_ACK if ok else PRP_NACK
        self.prp_tx(PRP_OPT_LOGIN_RESP, tx_flag=False, data=data, prio=True)

    def _rx_cmd_login_ack(self, payload: bytes):
        if self._is_ack(payload):
            logger.info(f"PRP: Login accepted !! UID: {self._uid}")
        else:
            self._set_remote_auth(False)  # oder direkt False setzen
            logger.warning(f"PRP: Login denied !! UID: {self._uid}")

    # =============================
    # ====== OPT-ID 25 - Logout Stuff
    def cmd_logout(self):
        """ Client sendet Logout """
        if not self.is_handshake:
            return
        self._state_manager.add_pending(PRP_OPT_LOGOUT, {'login_ok': False})
        self.prp_tx(PRP_OPT_LOGOUT, tx_flag=True, data=b'', prio=True)

    def _rx_cmd_logout(self):
        """ Server bestätigt Logout """
        print('Received Logout CMD')
        self._set_auth(False)
        self.prp_tx(PRP_OPT_LOGOUT, tx_flag=False, data=b'', prio=True)

    def _rx_cmd_logout_response(self):
        """ Client empfängt Logout bestätigung """
        print("LOGOUT erfolgreich!")
        self._set_auth(False)

    # =============================
    # == OPT-ID 26 - States Update via Remote / By Grok AI
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

    def rx_remote_state_update(self, payload: bytes):
        updates = self._state_manager.decode_payload(payload)
        if updates:
            self._response_state_update(updates)
            self._state_manager.update_own(updates)  # oder besser: self._state_manager.update_own(updates)
            logger.info(f"PRP: Dynamisches State-Update empfangen: {updates}")
            self._tx_resp_remote_state_update(success=True)
        else:
            self._tx_resp_remote_state_update(success=False)
        self._local_response_handler(PRP_OPT_STATE_UPDATE)

    # == Response
    def _tx_resp_remote_state_update(self, success: bool):
        """ TX Respond State Update (ACK) """
        data = PRP_ACK if success else PRP_NACK
        self.prp_tx(opt_id=PRP_OPT_STATE_UPDATE, tx_flag=False, data=data, prio=True)

    def rx_resp_remote_state_update(self, payload: bytes):
        """ RX Respond State Update (ACK) """
        if self._is_ack(payload):
            logger.info("PRP: Remote State-Update erfolgreich bestätigt.")
            logger.debug(f"PRP: Bestätige State Update: {self._uid}")
            for k, v in self._state_manager.remote.items():
                logger.debug(f"PRP: {k}:{v}")
        else:
            logger.warning(f"PRP: Remote State-Update fehlgeschlagen! - UID: {self._uid}")

    #####################################
    # Helper
    """
    def _check_version(self):
        cli     = self.cli
        if not hasattr(cli, 'stat_identifier'):
            logger.error(f"PRP: Attribute Error Version Check")
            return False
        stat_id = cli.stat_identifier
        if PRP_SW_RESTR not in stat_id.software:
            logger.warning(f"PRP: This function is just available with {PRP_SW_RESTR}. {stat_id.software}")
            return False
        if version_tuple(stat_id.version) < version_tuple(PRP_VER_RESTR):
            logger.warning(f"PRP: This function is just available with {PRP_SW_RESTR} Version:")
            logger.warning(f"PRP: Version >= {PRP_VER_RESTR}")
            return False
        return True
    """

    #####################################
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
    # GUI I/O
    # == Handshake
    def _gui_resp_handshake(self):
        # == GUI Response
        gui = self._get_gui()
        if not hasattr(gui, 'init_popt_remote'):
            return
        #
        gui.init_popt_remote(self._uid)
        #gui.init_popt_remote(self._remote_uid)

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

    def _send_cli_esc_recv_status(self):
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
    def _send_cli_esc_abort_sender_status(self):
        """
        TX.
        Sendet ABORT Mitteilung an gui.qso
        """
        status_msg = f"\nPRP ■ !ABORT!"
        self._send_cli_esc_status_to_QSO(status_msg, tx=True)


    def _send_cli_esc_abort_recv_status(self):
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

    #####################################
    # CLI I/O
    @property
    def cli(self):
        if not hasattr(self._connection, 'cli'):
            return None
        return self._connection.cli

    # == Handshake
    def init_prp_handshake(self, remote_identy):
        """ Bekommt Station Identy Objekt von CLI """
        self._handshake.init_from_cli(remote_identy)

    @property
    def is_handshake(self):
        return self._handshake.is_completed

    @property
    def is_handshake_pending(self):
        return self._handshake.is_pending

    # == CLI Abort
    def cli_abort(self):
        if not self.is_handshake:
            return False

        # == Prüfe ob CLI-ESC Pakte im TX-Buffer sind
        if not self._tx_buffer.is_prp_opt_id_in_tx_buff(PRP_OPT_ESC_CLI):
            return False
        # == Sende ABORT-RESP Frame
        self._rx_cmd_21()
        return True


