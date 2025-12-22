"""
(P)oPT (R)emote (P)rotocol
"""

from cfg.logger_config import logger
from fnc.ax25_fnc import reverse_uid
from prp.prp_auth_handler import PRPAuthHandler
from prp.prp_cli_stream_handler import PRPCLIStreamHandler
from prp.prp_const import PRP_OPT_21, PRP_OPT_LOGIN_RESP, PRP_OPT_LOGOUT, PRP_OPT_STATE_UPDATE, \
    PRP_OPT_ESC_CLI, PRP_RM_RESP_LOGOUT, PRP_RM_RESP_LOGIN
from prp.prp_control_handler import PRPControlHandler
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
        # == RX Processor
        self._rx_processor   = PRP_RX_Processor(self)
        # == CLI-ESC
        self._cli_esc        = PRPCLIStreamHandler(self)
        # == Protocol
        self._protocol       = PRPProtocolHandler(self)
        # == Control
        self._prp_control    = PRPControlHandler(self)
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

    @property
    def gui(self):
        return self._get_gui()

    # ==== PRP Classes
    @property
    def prp_tx_buffer(self):
        return self._tx_buffer

    @property
    def prp_rx_processor(self):
        return self._rx_processor

    @property
    def prp_protocol(self):
        return self._protocol

    @property
    def prp_remote_monitor(self):
        return self._remote_monitor

    @property
    def prp_state_manager(self):
        return self._state_manager

    @property
    def prp_handshake(self):
        return self._handshake

    @property
    def prp_auth(self):
        return self._prp_auth

    @property
    def prp_control(self):
        return self._prp_control

    @property
    def prp_cli_esc(self):
        return self._cli_esc

    #####################################
    # Tasker (ax25Conn)
    def tasker(self):
        """ Called fm ax25Conn """
        self._remote_monitor.task()
        return True

    #####################################
    # Response Handler
    def handle_response(self, opt_id: int, resp_ok=True):
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
        return self._cli_esc.send_cli_data(payload)

    # === CLI-ESC Status Meldungen für gui.QSO
    def get_cli_esc_sender_status(self):
        """
        TX.
        Gibt den Status eines gesendeten CLI-ESC-Frames zurück, falls vorhanden.
        """
        return self._cli_esc.get_sender_status()

    #####################################
    # Remote Monitor Stream - OPT 0 - 19
    def remote_monitor_update(self, ax25frame_conf: dict):
        """ Called fm port_handler > connection.update_monitor() """
        if (not self._state_manager.get_own('cli_rem_mon') and
            not self._state_manager.get_own('gui_rem_mon')):
            return
        self._remote_monitor.update(ax25frame_conf)

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
        self._prp_control.send_cli_esc_abort_request()
        return True

    # =============================
    # ====== OPT-ID 22 - Disconnect CMD
    def cmd_disco(self):
        """ TX Start Disco CMD """
        if not self.is_handshake:
            return
        self._prp_control.send_disconnect()
        # self.prp_tx(opt_id=PRP_OPT_DISCO, tx_flag=True, data=b'', prio=True)


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
