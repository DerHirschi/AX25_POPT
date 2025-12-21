from ax25.ax25Error import AX25DecodingERROR
from ax25.ax25dec_enc import bytearray2hexstr
from cfg.logger_config import logger
from fnc.crc_fnc import crc16_ccitt
from fnc.lzhuf import LZHUF_Comp
from prp.prp_const import PRP_FESC, PRP_FEND, PRP_FESC_TFESC, PRP_FESC_TFEND, PRP_FLAG, PRP_OPT_20, PRP_OPT_21, \
    PRP_OPT_DISCO, PRP_OPT_LOGIN_REQ, PRP_OPT_LOGIN_RESP, PRP_OPT_LOGOUT, PRP_OPT_STATE_UPDATE, PRP_OPT_ESC_CLI, \
    PRP_OPT_PRP_BATCH, PRP_DONT_ACK, PRP_NACK
from prp.prp_dec_fnc import pack_6bit_int_and_bool, unpack_6bit_int_and_bool


class PRPProtocolHandler:
    """
    Verantwortlich für:
    - Encoding und Decoding von PRP-Frames
    - Dispatching aller Control-Commands (OPT 20–63)
    - ACK/NACK-Handling
    """

    def __init__(self, prp_root):
        """
        :param prp_root: Referenz auf PRPremote-Instanz (für Zugriff auf _prp_rx_process, Status-Meldungen etc.)
        """
        self._prp_root       = prp_root

    # ===================================================================
    # Encoding
    # ===================================================================
    def encode_frame(self, opt_id: int, tx: bool, data: bytes, compress=True, send_uncompressed=True):
        send_compressed = False
        data_len        = len(data)
        comp_data_len   = len(data)
        if data:
            if compress:
                # LZHUF it
                lzhuf = LZHUF_Comp()
                compressed_data = lzhuf.encode(data)
                len_compressed = len(compressed_data)
                if len_compressed < data_len:
                    comp_data_len   = len_compressed
                    send_compressed = True
                    data = compressed_data
            # Wenn nicht zu komprimieren geht und nicht send_uncompressed, nicht senden!
            # Für CLI-ESC Mode
            if not send_compressed and not send_uncompressed:
                return None
            # Escaping
            data = data.replace(PRP_FESC, PRP_FESC_TFESC)
            data = data.replace(PRP_FEND, PRP_FESC_TFEND)

        # Meta Date für Status Msg
        self._prp_root.rx_processor.set_last_pack_meta((data_len, comp_data_len))
        # Building Packet
        data_to_send  = bytearray()
        data_to_send += pack_6bit_int_and_bool(value=int(opt_id), flag1=tx, flag2=send_compressed)
        data_to_send += len(data).to_bytes(2, 'little')
        data_to_send += data
        # CRC
        crc           = crc16_ccitt(data_to_send)   # 2 Bytes - little
        # Adding Flag and CRC / Flag + Packet + CRC
        data_to_send  = PRP_FLAG + data_to_send + crc

        return data_to_send

    # ===================================================================
    # Decoding + Dispatch
    # ===================================================================
    def decode_and_dispatch(self, data: bytes):
        """
        Dekodiert ein vollständiges PRP-Frame und dispatched es.
        Wird von _prp_rx_process() aufgerufen.
        Gibt CLI-Payload zurück (falls vorhanden).
        """
        opt_byte = data[2:3]
        # length = data[3:5] # little
        payload = data[5:-2]
        checksum = data[-2:]
        ################################################################
        # Checking Checksum
        crc16 = crc16_ccitt(data[2:-2])
        if crc16 != checksum:
            logger.error(f"PRP: Checksum Error - UID: {self._prp_root.uid}")
            logger.error(f"PRP: Packet CRC: {checksum} - Calc CRC: {crc16}")
            # logger.error(f"PRP: Packet CRC: {checksum.to_bytes(2, 'little')} - Calc CRC: {crc16.to_bytes(2, 'little')}")
            logger.error("PRP: PRP-Frame:")
            logger.error(f"PRP:   ORG: {data}")
            logger.error(f"PRP:   HEX: {bytearray2hexstr(data)}")
            raise EncodingWarning
        ################################################################
        # Unescaping
        payload = payload.replace(PRP_FESC_TFEND, PRP_FEND)
        payload = payload.replace(PRP_FESC_TFESC, PRP_FESC)
        ################################################################
        # Decoding OPT Byte
        opt_id, tx, is_compressed = unpack_6bit_int_and_bool(opt_byte)
        prp_payload_len = len(payload)
        if is_compressed:
            lzhuf = LZHUF_Comp()
            payload = lzhuf.decode(payload)
        # Frame Status
        self._prp_root.rx_processor.set_comp_pack_meta((opt_id, prp_payload_len, len(payload)))
        ################################################################
        # 0 - 19 = Port ID
        if opt_id < 20:
            try:
                mon_conf = self._prp_root._decode_remote_mon_frame(payload, opt_id, tx)
                self._prp_root.port_handler.handle_remote_monitor_rx(mon_conf, self._prp_root.uid)
                return b''
            except Exception as e:

                logger.warning(f"PRP Remote Monitor: Decoding error UID: {self._prp_root.uid}")
                logger.warning(e)
                logger.warning(f"PRP Frame HEX: {bytearray2hexstr(data)}")
                return b''

        ################################################################
        # TX = Send CMD(True) / Response CMD(False) /
        # 20 - 63 = CMD'S

        # =============================================
        # tx=False → Zentrale Response/ACK-Behandlung
        # Nur für PRP States !!
        # =============================================
        if not tx:
            ack = True
            if opt_id not in PRP_DONT_ACK:
                if payload == PRP_NACK:
                    ack = False
                if ack:
                    # ACK CFG und update Remote-States
                    self._prp_root._ack_pending_remote_states(opt_id)
                else:
                    # Optional: Pending löschen oder retry
                    self._prp_root._del_pending_remote_states(opt_id)
            # Response Handler / GUI Updates usw.
            self._prp_root._local_response_handler(opt_id, resp_ok=ack)

        # Command Dispatch
        handler_map = {
            PRP_OPT_20:             self._handle_handshake,
            PRP_OPT_21:             self._handle_abort,
            PRP_OPT_DISCO:          self._handle_disco,
            PRP_OPT_LOGIN_REQ:      self._handle_login_req,
            PRP_OPT_LOGIN_RESP:     self._handle_login_resp,
            PRP_OPT_LOGOUT:         self._handle_logout,
            PRP_OPT_STATE_UPDATE:   self._handle_state_update,
            PRP_OPT_ESC_CLI:        self._handle_cli_esc,
            PRP_OPT_PRP_BATCH:      self._handle_batch,
        }

        handler = handler_map.get(opt_id)
        if handler:
            return handler(tx, payload)

        logger.warning(f"PRP: Unknown OPT-ID({opt_id}) from {self._prp_root.uid}")
        logger.warning("PRP: Possibly older PoPT version?")
        return b''

    # ===================================================================
    # Individual Command Handlers
    # ===================================================================
    def _handle_handshake(self, tx, payload):
        """ Handshake 20 """
        if tx:
            self._prp_root._rx_cmd_20(payload)
        else:
            self._prp_root._rx_resp_cmd_20(payload)
        return b''

    def _handle_abort(self, tx, payload):
        """ PRP-Frame Abort - 21 """
        if tx:
            self._prp_root._rx_cmd_21()
        else:
            print(f"prp frame decoder: _rx_resp")
            # self._rx_resp_cmd_21()
            return b''
            # Optional: Status für Abort senden
            # if self._next_pack_meta[0] == PRP_OPT_ESC_CLI:  # Wenn vorheriges war CLI-ESC
            #    self._send_cli_esc_abort_recv_status()
        return b''

    def _handle_disco(self, tx, payload):
        """ Disconnect 22 """
        if tx:
            self._prp_root._rx_cmd_disco()
        return b''

    def _handle_login_req(self, tx, payload):
        """ Login Request 23 """
        if tx:
            self._prp_root._rx_cmd_login_request()
        else:
            self._prp_root._rx_cmd_login_challenge(payload)
        return b''

    def _handle_login_resp(self, tx, payload):
        """ Login Response 24 """
        if tx:
            self._prp_root._rx_cmd_login_response(payload)
        else:
            self._prp_root._rx_cmd_login_ack(payload)
        return b''

    def _handle_logout(self, tx, payload):
        """ Logout 25 """
        if tx:
            self._prp_root._rx_cmd_logout()
        else:
            self._prp_root._rx_cmd_logout_response()
        return b''

    def _handle_state_update(self, tx, payload):
        """ State Update 26 """
        if tx:
            self._prp_root._rx_remote_state_update(payload)
        else:
            self._prp_root._rx_resp_remote_state_update(payload)
        return b''

    def _handle_cli_esc(self, tx, payload):
        """ CLI Escape 62 """
        if tx:
            return self._prp_root._prp_rx_esc_cli(payload)
        else:
            pass
        return b''

    def _handle_batch(self, tx, payload):
        """ Batch Mode 63 """
        if tx:
            return self._prp_root._prp_rx_batch(payload)
        else:
            pass
        return b''

    # ===================================================================
    # Public TX Helpers (werden von PRPremote aufgerufen)
    # ===================================================================
    def send_command(self, opt_id: int, data: bytes = b'', prio: bool = False,
                     compress: bool = True, send_uncompressed: bool = True) -> bool:
        """
        Bequeme Methode zum Senden von Control-Commands.
        """
        return self._prp_root._prp_tx(opt_id=opt_id, tx_flag=True, data=data,
                                   prio=prio, compress=compress,
                                   send_uncompressed=send_uncompressed)

    def send_response(self, opt_id: int, data: bytes = b'', prio: bool = True):
        """
        Sendet eine Response (tx=False)
        """
        return self._prp_root._prp_tx(opt_id=opt_id, tx_flag=False, data=data, prio=prio)