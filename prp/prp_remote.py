"""
(P)oPT (R)emote (P)rotocol
"""
import copy
import datetime
import hashlib
import os
import time

from ax25.ax25Error import AX25DecodingERROR
from cfg.logger_config import logger
from cli.cliStationIdent import get_station_id_obj
from fnc.ax25_fnc import reverse_uid
from fnc.crc_fnc import crc16_ccitt
from fnc.lzhuf import LZHUF_Comp
from ax25.ax25dec_enc import AX25Frame, bytearray2hexstr
from fnc.str_fnc import version_tuple
from prp.prp_const import PRP_FESC, PRP_FESC_TFESC, PRP_FEND, PRP_FESC_TFEND, PRP_FLAG, PRP_DONT_ACK, PRP_NACK, \
    PRP_OPT_20, PRP_OPT_21, PRP_OPT_DISCO, PRP_OPT_LOGIN_REQ, PRP_OPT_LOGIN_RESP, PRP_OPT_LOGOUT, PRP_OPT_STATE_UPDATE, \
    PRP_OPT_ESC_CLI, PRP_OPT_PRP_BATCH, PRP_BATCH_MIN_PACK, PRP_BATCH_MAX_PAY, PRP_RM_RESP_LOGOUT, PRP_RM_RESP_LOGIN, \
    PRP_ACK, PRP_VER_RESTR, PRP_SW_RESTR, PRP_VER_RESTR_HANDSHAKE, PRP_ABORT_FRAME
from prp.prp_dec_fnc import pack_6bit_int_and_bool, unpack_6bit_int_and_bool, pack_time_hms, unpack_time_hms_to_datetime

DBUG_PW = 'test1234'

class ListBuffer:
    def __init__(self, thread_lock_timer=0.01):
        self._buffer: list      = []
        self._threadLock        = False
        self._threadLockTimer   = float(thread_lock_timer)

    def _get_thread_lock(self):
        while self._threadLock:
            time.sleep(self._threadLockTimer)
        self._threadLock = True

    def buffer_read(self):
        self._get_thread_lock()
        ret = self._buffer.pop(0)
        self._threadLock = False
        return ret

    def buffer_write(self, data):
        self._get_thread_lock()
        self._buffer.append(data)
        self._threadLock = False

    def buffer_clear(self):
        self._get_thread_lock()
        self._buffer = []
        self._threadLock = False

    # == Read Only / property
    @property
    def is_empty(self):
        return bool(not self._buffer)

    @property
    def length(self):
        return len(self._buffer)


class PRPremote:
    def __init__(self, port_handler, connection):
        # == Port Handler
        self._port_handler = port_handler
        self._get_gui      = lambda : self._port_handler.get_gui()

        # == Connection
        self._connection   = connection
        if self._connection.is_incoming_conn():
            self._uid          = str(reverse_uid(connection.uid))
        else:
            self._uid          = str(connection.uid)

        #################################
        # Decoding Resterampe
        self._rest_buffer  = bytearray()

        #################################
        # Helper PRP
        self._is_ack    = lambda payload: True if payload == PRP_ACK else False

        #################################
        # Meta Daten für QSO-Status Msg
        self._comp_pack_meta   = None  # RX (opt-id, prp-payload-len, payload-len) Zum Berechnen des der Größe des Restpaketes
        self._next_pack_meta   = None  # RX (opt-id, prp-payload-len) Zum Berechnen des der Größe des Restpaketes
        self._last_pack_meta   = None  # TX (org-payload-len, prp-pack-len) Für Status Meldungen

        #################################
        # Own States / States der eigenen Station
        self._own_states = dict(
            # == Handshake / Station Cap
            stat_identy     = None,     # Station Identy Obj / !! PRIVATE !!!

            # == Remote Monitor
            cli_rem_mon     = False,    # TODO Remote Monitor CLI Stream
            gui_rem_mon     = False,    # Remote Monitor Stream
            rem_mon_port    = 0,        # Port Filter
            rem_mon_incl    = [],       # Incl Filter
            rem_mon_excl    = [],       # Excl Filter

            # == Batch Mode / vorrest nur für Mon Stream
            batch_mode      = 'auto',   # 'auto', 'on', 'off'
            batch_wait      = 30,       # Sekunden Pakete sammeln

            # == Remote CTL/States
            cli_esc         = False,    # CLI-ESC Mode (sendet CLI Stream komprimiert)

            # == Login/Auth
            login_ok        = False,    # Auth OK / !! PRIVATE !!!
        )
        # == State I/O
        self._get_own_state    = lambda k     : self._own_states[k]
        self._set_own_state    = lambda k, val: self._own_states.update({k: val})
        self._update_own_state = lambda cfg   : self._own_states.update(cfg)

        # == !! PRIVATE STATES !!
        self._private_state    = ['login_ok', 'stat_identy']
        # == State I/O
        self._is_private_state = lambda state_key: state_key in self._private_state

        #################################
        # Remote States / Bestätigt States der Gegenstation
        self._remote_states       = copy.deepcopy(self._own_states)     # Kopie von _own_states
        # == State I/O
        self._get_remote_state    = lambda k     : self._remote_states[k]
        self._set_remote_state    = lambda k, val: self._remote_states.update({k: val})
        self._update_remote_state = lambda cfg   : self._remote_states.update(cfg)
        # == Für GUI / State I/O
        self._get_remote_states   = lambda       : dict(self._remote_states)

        #################################
        # == Remote States ACK
        self._pending_remote_states        = {}    # OPT ID, Remote-State CFG
        # == State I/O
        self._update_pending_remote_states = lambda opt_id, state_cfg: self._pending_remote_states.update({opt_id: state_cfg})
        self._get_pending_remote_state     = lambda opt_id           : self._pending_remote_states.get(opt_id, None)
        self._set_pending_remote_state     = lambda opt_id, state_key, val: self._pending_remote_states.update({opt_id: {state_key: val}})

        #################################
        # == Handshake
        self._is_handshake       = lambda    : False if self._get_remote_state('stat_identy') is None else True
        self._get_remote_identy  = lambda    : self._get_remote_state('stat_identy')
        self._set_remote_identy  = lambda val: self._set_remote_state('stat_identy', val)
        self._set_own_identy     = lambda val: self._set_own_state('stat_identy', val)
        # Eigenen Stat Identy setzen
        self._set_own_identy(self._get_own_stat_identy())

        #################################
        # Batch Mode
        # == CTL
        self._batch_buffer       = ListBuffer() # Buffer ax25frame_conf Buffer
        self._batch_timer        = time.time() + self._own_states.get('batch_wait', 30)
        # == Self / State I/O
        self._batch_wait         = lambda : self._own_states.get('batch_wait', 30)
        self._is_batch_mode      = lambda : True if self._own_states.get('batch_mode', 'auto') == 'on'   else False
        self._is_batch_mode_auto = lambda : True if self._own_states.get('batch_mode', 'auto') == 'auto' else False
        self._set_batch_mode     = lambda mode: self._own_states.update({'batch_mode': mode})
        # == Remote / State I/O
        # self._remote_is_batch_mode      = lambda: True if self._remote_states.get('batch_mode', 'auto') == 'on' else False
        # self._remote_is_batch_mode_auto = lambda: True if self._remote_states.get('batch_mode', 'auto') == 'auto' else False
        self._remote_set_batch_mode     = lambda mode: self._remote_states.update({'batch_mode': mode})

        #################################
        # CLI ESC / Komprimiert senden
        # == Self / State I/O
        self._is_cli_esc_mode         = lambda: self._own_states.get('cli_esc', False)
        self._set_cli_esc_mode        = lambda is_on: self._own_states.update({'cli_esc': is_on})
        # == Remote / State I/O
        self._remote_is_cli_esc_mode  = lambda: self._remote_states.get('cli_esc', False)
        self._remote_set_cli_esc_mode = lambda is_on: self._remote_states.update({'cli_esc': is_on})

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
        self._is_auth        = lambda        : self._own_states.get('login_ok', False)
        self._set_auth       = lambda is_auth: self._own_states.update({'login_ok': is_auth})
        # == Remote / State I/O
        self._is_remote_auth = lambda        : self._remote_states.get('login_ok', False)
        self._set_remote_auth= lambda is_auth: self._remote_states.update({'login_ok': is_auth})


    #####################################
    # Tasker (ax25Conn)
    def tasker(self):
        """ Called fm ax25Conn """
        self._remote_monitor_batch_update()
        return True

    #####################################
    # PRP ENC/DEC
    def _encode_prp_frame(self, opt_id: int, tx: bool, data: bytes, compress=True, send_uncompressed=True):
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
        self._last_pack_meta = data_len, comp_data_len
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

    def _decode_prp_frame(self, data: bytes):
        opt_byte = data[2:3]
        # length = data[3:5] # little
        payload  = data[5:-2]
        checksum = data[-2:]
        ################################################################
        # Checking Checksum
        crc16    = crc16_ccitt(data[2:-2])
        if crc16 != checksum:
            logger.error(f"PRP: Checksum Error - UID: {self._uid}")
            logger.error(f"PRP: Packet CRC: {checksum} - Calc CRC: {crc16}")
            #logger.error(f"PRP: Packet CRC: {checksum.to_bytes(2, 'little')} - Calc CRC: {crc16.to_bytes(2, 'little')}")
            logger.error( "PRP: PRP-Frame:")
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
        prp_payload_len           = len(payload)
        if is_compressed:
            lzhuf   = LZHUF_Comp()
            payload = lzhuf.decode(payload)
        # Frame Status
        self._comp_pack_meta = opt_id, prp_payload_len, len(payload)
        ################################################################
        # 0 - 19 = Port ID
        if opt_id in range(20):
            try:
                return self._decode_remote_mon_frame(payload, opt_id, tx), b''
            except AX25DecodingERROR:
                logger.warning("-------------------------------------------------------------------")
                logger.warning(f'PRP Remote Monitor: decoding UID: {self._uid}')
                logger.warning(f'PRP Remote Monitor: prp frame org {data}')
                logger.warning(f'PRP Remote Monitor: prp frame hex {bytearray2hexstr(data)}')
                logger.warning(f'PRP Remote Monitor: ax25_frame org {payload}')
                logger.warning(f'PRP Remote Monitor: ax25_frame hex {bytearray2hexstr(payload)}')
                logger.warning("-------------------------------------------------------------------")
                return None, b''

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
                    self._ack_pending_remote_states(opt_id)
                else:
                    # Optional: Pending löschen oder retry
                    self._del_pending_remote_states(opt_id)
            # Response Handler / GUI Updates usw.
            self._local_response_handler(opt_id, resp_ok=ack)

        # =============================================
        #  tx=True → das sind Commands vom Remote
        # =============================================

        """ Handshake 20 """
        if opt_id == PRP_OPT_20:
            if tx:
                self._rx_cmd_20(payload)
            else:
                self._rx_resp_cmd_20(payload)
            return None, b''

        """ PRP-Frame Abort - 21 """
        if opt_id == PRP_OPT_21:
            if tx:
                self._rx_cmd_21()
            else:
                print(f"prp frame decoder: _rx_resp")
                #self._rx_resp_cmd_21()
                return None, b''
                # Optional: Status für Abort senden
                #if self._next_pack_meta[0] == PRP_OPT_ESC_CLI:  # Wenn vorheriges war CLI-ESC
                #    self._send_cli_esc_abort_recv_status()
            return None, b''

        """ Disconnect 22 """
        if opt_id == PRP_OPT_DISCO:
            if tx:
                self._rx_cmd_disco()
            return None, b''

        """ Login Request 23 """
        if opt_id == PRP_OPT_LOGIN_REQ:
            if tx:
                self._rx_cmd_login_request()
            else:
                self._rx_cmd_login_challenge(payload)
            return None, b''

        """ Login Response 24 """
        if opt_id == PRP_OPT_LOGIN_RESP:
            if tx:
                self._rx_cmd_login_response(payload)
            else:
                self._rx_cmd_login_ack(payload)
            return None, b''

        """ Logout 25 """
        if opt_id == PRP_OPT_LOGOUT:
            if tx:
                self._rx_cmd_logout()
            else:
                self._rx_cmd_logout_response()
            return None, b''

        """ State Update 26 """
        if opt_id == PRP_OPT_STATE_UPDATE:
            if tx:
                self._rx_remote_state_update(payload)
            else:
                self._rx_resp_remote_state_update(payload)
            return None, b''

        """ CLI Escape 62 """
        if opt_id == PRP_OPT_ESC_CLI:
            if tx:
                return None, self._prp_rx_esc_cli(payload)
            else:
                pass
            return None, b''

        """ Batch Mode 63 """
        if opt_id == PRP_OPT_PRP_BATCH:
            if tx:
                return None, self._prp_rx_batch(payload)
            else:
                pass
            return None, b''
        """ OPT ID existiert nicht """
        logger.warning(f"PRP: Unknown OPT-ID({opt_id})")
        logger.warning( "PRP:    Perhaps you are using an older version of PopT,")
        logger.warning(f"PRP:    that does not support OPT({opt_id}) ?")
        return None, b''

    #####################################
    # PRP I/O - TX/RX
    def _prp_tx(self, opt_id: int, tx_flag: bool, data: bytes, prio=False, compress=True, send_uncompressed=True):
        data2send = self._encode_prp_frame(
            opt_id=opt_id,
            tx=tx_flag,
            data=data,
            compress=compress,
            send_uncompressed=send_uncompressed
        )
        if not data2send:
            # Lösche Meta Daten für Status Meldungen
            self._last_pack_meta = None
            return False

        # Abort Frames immer als Erstes senden
        abort = False
        if opt_id == PRP_OPT_21 and not tx_flag:
            print("TX ABORT Frame !!!!!")
            abort = True
        print(f"TX OPT-ID: {opt_id} - tx:{tx_flag}")
        # An AX25Conn senden
        self._connection.send_remote_data((opt_id, data2send), prio=prio, is_abort_frame=abort)
        return True

    def prp_rx(self, data: bytes):
        # Opt by Grok-AI
        # == Kombiniere mit Buffer, falls vorhanden
        if self._rest_buffer:
            data = self._rest_buffer + data
            self._rest_buffer = bytearray()

        rest_data  = bytearray()  # Sammelt den Non-Remote-Monitor-Stream
        data_len   = len(data)
        i = 0

        while i < data_len:

            # == Suche nächsten Frame-Start (8D 81)
            if data[i:i + 2] == PRP_FLAG:

                # == Potenzieller Frame-Start gefunden
                self._next_pack_meta = None
                if i + 5 > data_len:
                    # == Header unvollständig -> puffern
                    self._rest_buffer   = data[i:]
                    break

                # == Entpacke Header Daten
                opt_id, _, _ = unpack_6bit_int_and_bool(data[i + 2:i + 3])
                length       = int.from_bytes(data[i + 3:i + 5], 'little')
                frame_end    = i + 5 + length + 2  # Header(5)+ len+ CRC(2)

                # == Speicher Frame Status (CLI-ESC Meta)
                self._next_pack_meta = opt_id, length

                # ===============================================
                # == Potenziellen ABORT Frame im Datensatz suchen
                # PRP-Flag(2) + FLAG(2) + OPT(1) + LEN(2) + CRC(2)
                if frame_end > data_len: # Min 12 Bytes
                    try:
                        abort_index =  data[i + 2:].index(PRP_ABORT_FRAME)   # Kann nur nach normaler Flag kommen
                    except ValueError:
                        pass
                    else:
                        logger.info(f"PRP: Abort-Sequence im Payload gefunden. Verwerfe bereits empfangenes Paket")

                        self._send_cli_esc_abort_recv_status()  # Rufe immer, filter intern

                        self._comp_pack_meta = None
                        self._next_pack_meta = None
                        self._rest_buffer = bytearray()

                        # == Entferne ABORT aus data gegen Loop
                        full_abort_index = i + 2 + abort_index + len(PRP_ABORT_FRAME)
                        i                = full_abort_index
                        continue

                # == Immer noch kein komplettes PRP-Frame ?
                if frame_end > data_len:
                    # Frame unvollständig -> puffern
                    self._rest_buffer   = data[i:]
                    self._send_cli_esc_recv_status()
                    break

                # == Komplettes Frame extrahiert!
                rem_mon_pack = data[i:frame_end]

                try:
                    # == Process PRP-Frame
                    rest_data += self._prp_rx_process(rem_mon_pack)
                except EncodingWarning:
                    logger.debug("PRP: Data Chunk:")
                    logger.debug(f"PRP:   DATA  : {data}")
                    logger.debug(f"PRP:   DATA H: {bytearray2hexstr(data)}")
                    logger.debug(f"PRP:   REST  : {rest_data}")
                    logger.debug(f"PRP:   REST H: {bytearray2hexstr(rest_data)}")

                self._next_pack_meta = None
                # == Springe zum nächsten Byte nach dem Frame
                i = frame_end
                continue

            # =================== KEIN FRAME ===================
            rest_data.append(data[i])
            i += 1

        # Wenn Rest nach letztem Frame übrig zu rest_data hinzufügen (aber hier schon in Schleife gehandhabt)
        if rest_data == PRP_FEND:   # == 8D ?
            self._rest_buffer  += rest_data
            return b''

        return bytes(rest_data)

    # ====== Processing PRP-Frame
    def _prp_rx_process(self, rem_mon_frame: bytes):
        try:
            decoded_ax25pack, cli_payload = self._decode_prp_frame(rem_mon_frame)
        except EncodingWarning as ex:
            raise ex
        if decoded_ax25pack:
            # TODO Failsafe Response handler self._set_remote_state('gui_rem_mon', True)
            # GUI Handling - Remote Monitor Frame
            if not hasattr(self._port_handler, 'handle_remote_monitor_rx'):
                logger.error("Attribute Error Port-Handler: handle_remote_monitor_rx ")
                return cli_payload
            self._port_handler.handle_remote_monitor_rx(decoded_ax25pack, self._uid)
        return cli_payload

    # ====== PRP Batch Mode I/O
    def _prp_batch_tx(self, prp_frames):
        """ Fasst mehrere PRP-Frames zu einem komprimierten Frame zusammen """
        if not prp_frames:
            return

        batch_data = bytearray()
        n = 0
        for prp_frame in prp_frames:
            batch_data += prp_frame
            n          += 1
            # Max Rohdaten Größe erreicht ?
            batch_data_len = len(batch_data)
            if (batch_data_len >= PRP_BATCH_MAX_PAY and
                len(prp_frames) - n > PRP_BATCH_MIN_PACK) :
                data2send = self._encode_prp_frame(opt_id=PRP_OPT_PRP_BATCH, tx=True, data=batch_data, compress=True)
                if not data2send:
                    batch_data = bytearray()
                    continue
                logger.debug(f"Sende Batch len      : {len(batch_data)} Bytes")
                logger.debug(f"Sende Batch-Paket len: {len(data2send)} Bytes")
                logger.debug(f"Comp Ratio           : {len(batch_data) / len(data2send)}")
                self._connection.send_remote_data((PRP_OPT_PRP_BATCH, data2send), prio=False)
                batch_data = bytearray()
        # Und den Rest
        if batch_data:
            data2send = self._encode_prp_frame(opt_id=PRP_OPT_PRP_BATCH, tx=True, data=batch_data, compress=True)
            if not data2send:
                return
            logger.debug(f"Sende Batch Rest len      : {len(batch_data)} Bytes")
            logger.debug(f"Sende Batch-Paket Rest len: {len(data2send)} Bytes")
            logger.debug(f"Comp Ratio Rest           : {len(batch_data) / len(data2send)}")
            self._connection.send_remote_data((PRP_OPT_PRP_BATCH, data2send), prio=False)

    def _prp_rx_batch(self, payload: bytes):
        """ Empfange PRP-Paket Batch """
        data_len  = len(payload)
        i         = 0
        cli_data  = bytearray() # CLI ESC Data
        while i < data_len:
            if payload[i:i + 2] != PRP_FLAG:
                logger.warning("PRP-Batch: PRP_FLAG not found in Datastream")
                logger.warning(f" Payload HEX: {bytearray2hexstr(payload)}")
                logger.warning(f" Index      : {i}")
                i += 1
                continue
            length    = int.from_bytes(payload[i + 3:i + 5], 'little')
            #        Header(5)+ len+ CRC(2)
            frame_end = i + 5 + length + 2
            # Komplettes Frame extrahiert!
            rem_mon_pack = payload[i:frame_end]
            try:
                cli_data += self._prp_rx_process(rem_mon_pack)
            except EncodingWarning:
                logger.warning("PRP-Batch: Data Chunk:")
                logger.warning(f" Payload HEX: {bytearray2hexstr(payload)}")
                logger.warning(f" Index      : {i}")
            # Springe zum nächsten Byte nach dem Frame
            i = frame_end

        return cli_data

    # ====== CLI Escape I/O
    def _prp_rx_esc_cli(self, payload: bytes):
        """ Empfange CLI Escape """
        # Frame Status . Kompletter CLI-ESC Frame
        self._send_cli_esc_recv_status()
        return payload

    def prp_tx_esc_cli(self, payload: bytes):
        """ Sende CLI Escape - AX25Conn.send_data() """
        # ESC-CLI Mode ist deaktiviert
        if not self._is_cli_esc_mode():
            return False
        # Wird nur gesendet, wenn es sich lohnt (Komprimierung)
        send_as_prp = self._prp_tx(opt_id=PRP_OPT_ESC_CLI,
                                   tx_flag=            True,
                                   data=               payload,
                                   prio=               True,
                                   compress=           True,
                                   send_uncompressed=  False
                                   )
        # Wenn gesendet nicht gesendet, lösche Metadaten für Status MSG
        if not send_as_prp:
            self._last_pack_meta = None
        # Zurück zur AX25Conn.send_data()
        return send_as_prp

    #####################################
    # Remote State ACK I/O
    def _ack_pending_remote_states(self, opt_id: int):
        if opt_id not in self._pending_remote_states:
            logger.error(
                f"RPR: ACK-BufferError: OPT-ID({opt_id}) nicht gefunden in self._pending_remote_states.")
            logger.error("RPR:   self._pending_remote_states:")
            for k, val in self._pending_remote_states.items():
                logger.error(f"RPR:   {k}: {val}")
            return
        # Hole cfg aus ACK-Buffer
        ack_cfg = self._pending_remote_states[opt_id]
        # Update Remote States
        self._update_remote_state(ack_cfg)
        # Lösche aus Pending Buffer
        del self._pending_remote_states[opt_id]

    def _add_pending_remote_states_cfg(self, opt_id: int, rem_state_cfg: dict):
        if opt_id in self._pending_remote_states:
            logger.warning(f"PRP: OPT-ID({opt_id}) ist bereit im AXK-Buffer")
            logger.warning(f"PRP:   CFG im Buffer: {self._pending_remote_states[opt_id]}")
            logger.warning(f"PRP:   Neue CfFG    : {rem_state_cfg}")
        # Erstmal überschreiben
        self._update_pending_remote_states(opt_id, rem_state_cfg)

    def _del_pending_remote_states(self, opt_id: int):
        if opt_id not in self._pending_remote_states:
            return
        del self._pending_remote_states[opt_id]

    #####################################
    # Remote Monitor Stream - OPT 0 - 19
    def remote_monitor_update(self, ax25frame_conf: dict):
        """ Called fm port_handler > connection.update_monitor() """
        if (not self._get_own_state('cli_rem_mon') and
            not self._get_own_state('gui_rem_mon')):
            return

        port_id = ax25frame_conf.get('port', -1)
        if port_id != self._get_own_state('rem_mon_port'):
            return

        from_call   = ax25frame_conf.get('from_call_str', '')
        to_call     = ax25frame_conf.get('to_call_str', '')
        frame_uid   = ax25frame_conf.get('uid', '')
        my_uid      = str(self._uid)
        my_uid_rev  = reverse_uid(my_uid)
        incl_filter = self._get_own_state('rem_mon_incl')
        excl_filter = self._get_own_state('rem_mon_excl')

        # Own Connection Filter
        if frame_uid == my_uid or frame_uid == my_uid_rev:
            return

        if (
            (to_call   == self._connection.to_call_str_add and
            from_call  == self._connection.my_call_str_add)
            or
            (from_call == self._connection.to_call_str_add and
             to_call   == self._connection.my_call_str_add)
            ): return

        # Exclude Filter
        if (from_call in excl_filter or
            to_call   in excl_filter):
            return

        # Include Filter
        if incl_filter:
            if (
                not from_call in incl_filter and
                not to_call   in incl_filter
            ): return

        # CLI Monitor Stream Output
        if self._get_own_state('cli_rem_mon'):
            # TODO
            self._connection.cli.cli_update_monitor(ax25frame_conf)

        # Batch Mode
        if (self._is_batch_mode() or
           # Wenn schon etwas im batch-tx-buffer ist ansonsten Sequenz fehler
           not self._batch_buffer.is_empty or
           # Auto Batch Mode
           (self._is_batch_mode_auto() and not self._connection.can_send_next_prp_batch())
        ):
            self._batch_buffer.buffer_write(ax25frame_conf)
            return

        # PoPT Remote Monitor GUI
        if self._get_own_state('gui_rem_mon'):
            self._encode_remote_mon_frame(ax25frame_conf)

    def _remote_monitor_batch_update(self):
        """ Batch Mode Task """
        if self._batch_buffer.is_empty:
            # Timer resetten, wenn keine Pakete gesammelt wurde
            self._batch_timer = time.time() + self._batch_wait()
            return

        # Buffer Limit
        is_buffer_limit = True if self._batch_buffer.length > 30 else False

        # Nicht Task Timer und nicht Buffer-Limit
        if self._batch_timer > time.time() and not is_buffer_limit:
            return

        # Sammeln, solange AX25Conn noch was zum Senden hat
        if not self._connection.can_send_next_prp_batch() and not is_buffer_limit:
            return

        # Reset Task Timer
        self._batch_timer = time.time() + self._batch_wait()

        # Send as Batch or Single ?
        batch_len     = self._batch_buffer.length
        send_as_batch = False if batch_len <= PRP_BATCH_MIN_PACK else True

        batch_data: list[bytes] = []
        while not self._batch_buffer.is_empty:
            ax25frame = self._batch_buffer.buffer_read()
            # Batch zu klein. Sende Frames einzeln
            if not send_as_batch:
                # Auto Compressed
                self._encode_remote_mon_frame(ax25frame)
                continue

            # PoPT Remote Monitor
            ax25_rawFrame = ax25frame.get('ax25_raw', b'')
            port_id       = ax25frame.get('port', -1)
            tx            = ax25frame.get('tx', False)
            rx_time       = ax25frame.get('rx_time', datetime)
            dec_rx_time   = pack_time_hms(rx_time)
            ax25_data   = bytearray()
            ax25_data  += dec_rx_time
            ax25_data  += ax25_rawFrame
            batch_data.append(self._encode_prp_frame(opt_id=int(port_id), tx=tx, data=ax25_data, compress=False))

        if batch_data:
            self._prp_batch_tx(batch_data)

    def _encode_remote_mon_frame(self, ax25frame_conf: dict):
        ax25_rawFrame = ax25frame_conf.get('ax25_raw', b'')
        tx            = ax25frame_conf.get('tx', False)
        port_id       = ax25frame_conf.get('port', 0)
        rx_time       = ax25frame_conf.get('rx_time', datetime)
        dec_rx_time   = pack_time_hms(rx_time)
        ax25_data  = bytearray()
        ax25_data += dec_rx_time
        ax25_data += ax25_rawFrame
        self._prp_tx(opt_id=int(port_id), tx_flag=tx, data=ax25_data, prio=False)

    @staticmethod
    def _decode_remote_mon_frame(ax25_data, port_id, tx):
        rx_time = unpack_time_hms_to_datetime(ax25_data[:3])
        payload = ax25_data[3:]
        ax25frame = AX25Frame()
        try:
            ax25frame.decode_ax25frame(payload)
        except AX25DecodingERROR:
            raise AX25DecodingERROR
        ax25frame_conf = ax25frame.get_frame_conf()
        ax25frame_conf['tx']      = tx
        ax25frame_conf['rx_time'] = rx_time
        ax25frame_conf['port']    = port_id
        return ax25frame_conf

    # == Remote Monitor ABORT
    def _remote_monitor_abort(self):
        """ TX Respond CMD 21 - ABORT RESP - Wird in unvollständig empfangenen PRP-Frame gesucht """
        logger.debug(f"PRP: Remote Monitor Abort gesendet...")
        if hasattr(self._connection, 'prp_del_rem_mon_buff'):
            logger.debug(f"PRP: Lösche TX-Buffer und sende Abort RESP Frame: {self._uid}")
            # == Lösche Batch Buffer
            self._batch_buffer.buffer_clear()
            # == Lösche AX25Conn sende Buffer PRP-BATCH Frames
            self._connection.prp_del_rem_mon_buff(PRP_OPT_PRP_BATCH)  ########
            # == Sende Abort Frame
            self._tx_resp_cmd_21()
            return
            # == Sollte nicht passieren
        logger.error(f"PRP: AttributeError _prp_abort_all: {self._uid}")

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
        if self._has_own_state_changed(state_update,  'gui_rem_mon'):
            # == Remote Monitor STOP
            if not state_update['gui_rem_mon']:
                # == Lösche TX-Buffer & sende ABORT-Resp
                self._remote_monitor_abort()
                return
        # == CLI-ESC Sync
        if self._has_own_state_changed(state_update,  'cli_esc'):
            # == Sync CLI-ESC Own State with remote State
            self._set_remote_state('cli_esc', state_update['cli_esc'])

    #####################################
    # CTL CMD's - OPT 20 - 63
    #
    # =============================
    # OPT-ID 26 - States Update via Remote / By Grok AI
    def send_remote_state_update(self, state_updates: dict):
        # send_remote_state_update({'batch_mode': 'off', 'cli_esc': True})
        if not self._is_handshake():
            return False

        # update abgleichen mit _remote_states was sich geändert hat
        update_to_send = {}
        for k, v in state_updates.items():
            if k not in self._remote_states:
                continue
            if self._get_remote_state(k) != v:
                update_to_send[k] = v
        # Keine Updates?
        if not update_to_send:
            return False

        # Logger
        logger.debug(f"PRP: Sende State Update: {self._uid}")
        for k, v in update_to_send.items():
            logger.debug(f"PRP: {k}:{v}")

        # Pending für ACK
        self._add_pending_remote_states_cfg(PRP_OPT_STATE_UPDATE, update_to_send)

        bin_payload = self._encode_state_updates(update_to_send)
        if not bin_payload:
            return False

        return self._prp_tx(
            opt_id=PRP_OPT_STATE_UPDATE,
            tx_flag=True,
            data=bin_payload,
            prio=True,
            compress=True
        )

    def _rx_remote_state_update(self, payload: bytes):
        i = 0
        updates = {}

        while i + 2 < len(payload):
            key_id = payload[i]
            val_len = payload[i + 1]
            i += 2
            if i + val_len > len(payload):
                break

            key = self._get_state_key_by_id(key_id)
            if not key:
                i += val_len
                continue

            # Sensible Keys blockieren
            if key == 'login_ok':
                logger.warning("PRP: Remote versucht login_ok zu ändern – ignoriert!")
                i += val_len
                continue

            value_data = payload[i:i + val_len]
            # Dekodierung mit Key-Name
            # == bool
            if key in ['cli_rem_mon', 'gui_rem_mon', 'cli_esc', 'login_ok']:
                value = bool(value_data[0])
            # == int 1 Byte / 256
            elif key == 'rem_mon_port':
                value = value_data[0]
            # == int 2 Bytes - little
            elif key == 'batch_wait':
                value = int.from_bytes(value_data, 'little')
            # == dict batch mode
            elif key == 'batch_mode':
                modes = {0: 'auto', 1: 'on', 2: 'off'}
                value = modes.get(value_data[0], 'auto')
            # == list
            elif key in ['rem_mon_incl', 'rem_mon_excl']:
                if len(value_data) < 2 or value_data[-2:] != b'\x00\x00':
                    value = []  # Korrupte Daten
                else:
                    parts = value_data[:-2].split(b'\x00')
                    value = [p.decode('UTF-8', 'ignore') for p in parts if p]
            else:
                i += val_len
                continue

            updates[key] = value
            i += val_len

        if updates:
            # Checke updates auf bestimmte Änderungen und führe Action aus
            self._response_state_update(state_update=updates)
            # Eigene States updaten
            self._update_own_state(updates)
            logger.info(f"PRP: Dynamisches State-Update empfangen: {updates}")
            # Update GUI
            self._local_response_handler(PRP_OPT_STATE_UPDATE)
            # Send Response
            self._tx_resp_remote_state_update(success=True)
        else:
            self._tx_resp_remote_state_update(success=False)

    # == Encoding
    def _encode_state_updates(self, state_updates: dict):
        payload      = bytearray()
        ordered_keys = list(self._own_states.keys())  # Fixe Reihenfolge

        for key, value in state_updates.items():
            if key not in ordered_keys:
                continue  # Unbekannter oder nicht erlaubter Key

            # Sensible Keys explizit verbieten (z.B. login_ok darf nicht remote gesetzt werden!)
            if self._is_private_state(key):
                logger.warning(f"PRP: Versuch, sensiblen State '{key}' remote zu ändern – blockiert!")
                continue

            key_id = ordered_keys.index(key)
            value_bytes = self._encode_state_value(key, value)  # Key-Name statt ID übergeben
            if value_bytes is None:
                continue

            payload.append(key_id)                    # 1 Byte ID
            payload.append(len(value_bytes))          # 1 Byte Länge
            payload.extend(value_bytes)

        return bytes(payload)

    @staticmethod
    def _encode_state_value(key: str, value):
        # == bool
        if key in ['cli_rem_mon', 'gui_rem_mon', 'cli_esc', 'login_ok']:
            return bytes([0x01 if value else 0x00])

        # == int 1 Byte / 256
        elif key == 'rem_mon_port':
            return bytes([value & 0xFF])

        # == int 2 Bytes - little
        elif key == 'batch_wait':
            return value.to_bytes(2, 'little')

        # == dict batch mode
        elif key == 'batch_mode':
            modes = {'auto': 0, 'on': 1, 'off': 2}
            return bytes([modes.get(value, 0)])

        # == list
        elif key in ['rem_mon_incl', 'rem_mon_excl']:
            if not value:
                return b'\x00\x00'  # Leere Liste
            data = '\x00'.join(value).encode('UTF-8', 'ignore')
            return data + b'\x00\x00'

        return None  # Unbekannter Key

    # == Response
    def _tx_resp_remote_state_update(self, success: bool):
        """ TX Respond State Update (ACK) """
        data = PRP_ACK if success else PRP_NACK
        self._prp_tx(opt_id=PRP_OPT_STATE_UPDATE, tx_flag=False, data=data, prio=True)

    def _rx_resp_remote_state_update(self, payload: bytes):
        """ RX Respond State Update (ACK) """
        if self._is_ack(payload):
            logger.info("PRP: Remote State-Update erfolgreich bestätigt.")
            logger.debug(f"PRP: Bestätige State Update: {self._uid}")
            for k, v in self._remote_states.items():
                logger.debug(f"PRP: {k}:{v}")
        else:
            logger.warning(f"PRP: Remote State-Update fehlgeschlagen! - UID: {self._uid}")

    # == Helper
    def _get_state_key_by_id(self, key_id: int):
        """ Gibt ID von self._own_states.keys() zurück."""
        keys = list(self._own_states.keys())
        if 0 <= key_id < len(keys):
            return keys[key_id]
        return None

    # =============================
    # ====== OPT-ID 20 - Handshake (ERWEITERT UM STATES)
    def send_cmd_20(self, short_format=False):
        """ TX CMD 20 - Handshake senden + öffentliche own_states """
        own_stat_identy = self._get_own_stat_identy()
        if not hasattr(own_stat_identy, 'id_str'):
            logger.error(f"PRP: Error Send Handshake. Kein eigener Station Identy !")
            return

        logger.info(f"PRP: Sende Handshake mit States: {self._uid}")

        self._set_own_identy(own_stat_identy)

        identy_str   = str(own_stat_identy.id_str)
        identy_bytes = identy_str.encode('ASCII', 'ignore')

        # Kurzes Format.. Nur Identy Str
        if short_format:
            self._prp_tx(opt_id=PRP_OPT_20, tx_flag=True, data=identy_bytes, prio=True)
            return

        # Öffentliche States anhängen
        states_bytes = self._encode_public_states()

        # Kombinieren: identy || 0x00 || states
        data = identy_bytes + b'\x00' + states_bytes

        self._prp_tx(opt_id=PRP_OPT_20, tx_flag=True, data=data, prio=True)

    def _tx_resp_cmd_20(self, success: bool, short_format=False):
        """ TX Respond CMD 20 - Handshake Response + öffentliche own_states """
        if not success:
            self._set_remote_identy(None)
            self._prp_tx(opt_id=PRP_OPT_20, tx_flag=False, data=PRP_NACK, prio=True)
            return

        own_stat_identy = self._get_own_stat_identy()
        if not hasattr(own_stat_identy, 'id_str'):
            self._prp_tx(opt_id=PRP_OPT_20, tx_flag=False, data=PRP_NACK, prio=True)
            return

        identy_str   = str(own_stat_identy.id_str)
        identy_bytes = identy_str.encode('ASCII', 'ignore')
        # Kurzes Format
        if short_format:
            self._prp_tx(opt_id=PRP_OPT_20, tx_flag=False, data=identy_bytes, prio=True)
            return

        # Langes Format - Mit State update
        states_bytes = self._encode_public_states()

        data = identy_bytes + b'\x00' + states_bytes

        self._prp_tx(opt_id=PRP_OPT_20, tx_flag=False, data=data, prio=True)

    def _rx_cmd_20(self, payload: bytes):
        """ RX CMD 20 - Handshake + States """
        # == Altes Format / kurzes Format
        if b'\x00' not in payload:
            logger.info(f"PRP: Handshake-Aufforderung ohne States empfangen(kurzes Format).– UID: {self._uid}")
            try:
                stat_identy_str = payload.decode('ASCII')
            except UnicodeDecodeError:
                logger.error(f"PRP: Handshake UnicodeDecodeError (Identy) – UID: {self._uid}")
                self._tx_resp_cmd_20(False)
                return
            stat_identy = get_station_id_obj(stat_identy_str)
            if stat_identy is None:
                logger.warning(f"PRP: Ungültiger Handshake (Identy) – UID: {self._uid}")
                self._tx_resp_cmd_20(False)
                return

            logger.info(f"PRP: Handshake akzeptiert – Version: {stat_identy.software} {stat_identy.version}")
            self._set_remote_identy(stat_identy)
            self._gui_resp_handshake()
            self._tx_resp_cmd_20(True, short_format=True)
            return

        logger.info(f"PRP: Handshake-Aufforderung mit States – UID: {self._uid}")
        # == Neu mit States
        identy_part, states_part = payload.split(b'\x00', 1)

        try:
            stat_identy_str = identy_part.decode('ASCII')
        except UnicodeDecodeError:
            logger.error(f"PRP: Handshake UnicodeDecodeError (Identy) – UID: {self._uid}")
            self._tx_resp_cmd_20(False)
            return

        stat_identy = get_station_id_obj(stat_identy_str)
        if stat_identy is None:
            logger.warning(f"PRP: Ungültiger Handshake (Identy) – UID: {self._uid}")
            self._tx_resp_cmd_20(False)
            return

        self._set_remote_identy(stat_identy)

        # States verarbeiten (falls vorhanden)
        if states_part:
            updates = self._decode_state_payload(states_part)
            if updates:
                self._update_remote_state(updates)
                logger.info(f"PRP: Initiale Remote-States aus Handshake übernommen: {updates}")

        logger.info(f"PRP: Handshake akzeptiert – Version: {stat_identy.software} {stat_identy.version}")
        self._gui_resp_handshake()
        self._tx_resp_cmd_20(True)

    def _rx_resp_cmd_20(self, payload: bytes):
        """ RX Respond CMD 20 - Handshake Response + States """
        if payload == PRP_NACK:
            logger.warning(f"PRP: Handshake abgelehnt von Gegenstation – UID: {self._uid}")
            self._set_remote_identy(None)
            return False

        if b'\x00' not in payload:
            logger.info(f"PRP: Handshake-Response ohne States (kurzes Format) – UID: {self._uid}")
            try:
                stat_identy_str = payload.decode('ASCII')
            except UnicodeDecodeError:
                logger.error(f"PRP: Handshake-Response UnicodeDecodeError – UID: {self._uid}")
                self._set_remote_identy(None)
                return False

            stat_identy = get_station_id_obj(stat_identy_str)
            if stat_identy is None:
                logger.error(f"PRP: Ungültiger Handshake-Response (Identy) – UID: {self._uid}")
                self._set_remote_identy(None)
                return False

            self._set_remote_identy(stat_identy)
            self._gui_resp_handshake()
            logger.info(f"PRP: Handshake erfolgreich – UID: {self._uid}")
            logger.info(f"PRP:   Gegenstation: {stat_identy.software} Ver. {stat_identy.version}")
            return True

        # == Langes Format - mit States
        identy_part, states_part = payload.split(b'\x00', 1)

        try:
            stat_identy_str = identy_part.decode('ASCII')
        except UnicodeDecodeError:
            logger.error(f"PRP: Handshake-Response UnicodeDecodeError – UID: {self._uid}")
            self._set_remote_identy(None)
            return False

        stat_identy = get_station_id_obj(stat_identy_str)
        if stat_identy is None:
            logger.error(f"PRP: Ungültiger Handshake-Response (Identy) – UID: {self._uid}")
            self._set_remote_identy(None)
            return False

        self._set_remote_identy(stat_identy)
        # States verarbeiten
        if states_part:
            updates = self._decode_state_payload(states_part)
            if updates:
                self._update_remote_state(updates)
                logger.info(f"PRP: Initiale Remote-States aus Handshake-Response übernommen: {updates}")

        self._gui_resp_handshake()
        logger.info(f"PRP: Handshake erfolgreich – UID: {self._uid}")
        logger.info(f"PRP:   Gegenstation: {stat_identy.software} Ver. {stat_identy.version}")
        return True

    # =============================
    # Neue Hilfsfunktionen für State-Transfer im Handshake

    def _encode_public_states(self):
        """
        Serialisiert alle own_states AUSSER private States.
        Verwendet exakt dasselbe Format wie _encode_state_updates().
        """
        payload      = bytearray()
        ordered_keys = list(self._own_states.keys())

        for key in ordered_keys:
            if self._is_private_state(key):
                continue  # login_ok und stat_identy NICHT senden!

            value = self._get_own_state(key)
            value_bytes = self._encode_state_value(key, value)
            if value_bytes is None:
                continue

            key_id = ordered_keys.index(key)
            payload.append(key_id)
            payload.append(len(value_bytes))
            payload.extend(value_bytes)

        return bytes(payload)

    def _decode_state_payload(self, payload: bytes):
        """
        Dekodiert ein State-Payload (wie bei OPT 26 oder Handshake).
        Gibt Dict mit Updates zurück (nur öffentliche Keys).
        """
        i = 0
        updates = {}

        while i + 2 < len(payload):
            key_id = payload[i]
            val_len = payload[i + 1]
            i += 2
            if i + val_len > len(payload):
                break

            key = self._get_state_key_by_id(key_id)
            if not key:
                i += val_len
                continue

            # Private States hier ebenfalls ignorieren (Sicherheit)
            if self._is_private_state(key):
                logger.warning(f"PRP: Handshake enthält privaten State '{key}' – ignoriert!")
                i += val_len
                continue

            value_data = payload[i:i + val_len]

            if key in ['cli_rem_mon', 'gui_rem_mon', 'cli_esc']:
                value = bool(value_data[0])
            elif key == 'rem_mon_port':
                value = value_data[0]
            elif key == 'batch_wait':
                value = int.from_bytes(value_data, 'little')
            elif key == 'batch_mode':
                modes = {0: 'auto', 1: 'on', 2: 'off'}
                value = modes.get(value_data[0], 'auto')
            elif key in ['rem_mon_incl', 'rem_mon_excl']:
                if len(value_data) < 2 or value_data[-2:] != b'\x00\x00':
                    value = []
                else:
                    parts = value_data[:-2].split(b'\x00')
                    value = [p.decode('UTF-8', 'ignore') for p in parts if p]
            else:
                i += val_len
                continue

            updates[key] = value
            i += val_len

        return updates

    # =============================
    # ====== OPT-ID 21 - ABORT
    def send_cmd_21(self):
        """ TX CMD 21 - CLI-ESC ABORT """
        if not self._is_handshake():
            return


        # == PRP ABORT-FRAME Senden
        self._prp_tx(opt_id=PRP_OPT_21, tx_flag=True, data=b'', prio=True)

    def _rx_cmd_21(self):
        """ RX CMD 21 - ABORT - CLI-ESC Abort """
        logger.info(
            f"PRP: Abort-REQ(CLI-ESC) empfangen (OPT-ID 21). Breche das Senden ab und lösche TX-Buffer. UID: {self._uid}")
        # == Status MSG to GUI ????????
        self._send_cli_esc_abort_sender_status()
        # == ESC-CLI Frame aus ax25Conn PRP-Rest-buffer löschen
        if hasattr(self._connection, 'prp_del_frame_buff_cli_esc'):
            logger.debug(f"PRP: Lösche TX-Buffer (aktuellen Frame)und sende Abort RESP Frame: {self._uid}")
            # == Lösche AX25Conn sende Buffer (nut tx-buffer, nicht prp-q buffer)
            self._connection.prp_del_frame_buff_cli_esc(PRP_OPT_ESC_CLI) # FIXME. Delete CLI-ESC Frames in prp-Q as well
            # == Send Response
            self._tx_resp_cmd_21()
            return
        logger.error(f"PRP: AttributeError _prp_abort_current_frame: {self._uid}")

    def _tx_resp_cmd_21(self):
        """ TX Respond CMD 21 - ABORT RESP - Wird in unvollständig empfangenen PRP-Frame gesucht """
        # == Sende Abort Frame
        self._prp_tx(opt_id=PRP_OPT_21, tx_flag=False, data=b'', prio=True)


    def _rx_resp_cmd_21(self):
        """ RX Respond CMD 21 """
        logger.info(
            f"PRP: Abort-Frame empfangen (OPT-ID 21). Breche Empfang ab und lösche Rest-Buffer. UID: {self._uid}")

    # =============================
    # ====== Disconnect CMD
    def cmd_disco(self):
        """ TX Start Disco CMD """
        if not self._is_handshake():
            return
        self._prp_tx(opt_id=PRP_OPT_DISCO, tx_flag=True, data=b'', prio=True)

    def _rx_cmd_disco(self):
        """ RX Start Disco CMD """
        # == Remote Monitor abschalten
        self._set_own_state('gui_rem_mon', False)
        self._set_own_state('cli_rem_mon', False)
        # == TX-Buffer löschen
        self._connection.prp_del_rem_mon_buff(None)
        # == Connection Disco
        self._connection.conn_disco()

    # =============================
    # ====== Login Stuff
    def cmd_login_request(self, password: str):
        """Client fordert Login-Challenge an"""
        if not self._is_handshake():
            return
        # TODO Password fm DB or GUI
        self._password_hash = hashlib.sha256(DBUG_PW.encode()).digest()
        self._add_pending_remote_states_cfg(PRP_OPT_LOGIN_RESP, {'login_ok': True})
        self._prp_tx(PRP_OPT_LOGIN_REQ, tx_flag=True, data=b'', prio=True)

    def _rx_cmd_login_request(self):
        """Client fordert Login-Challenge an"""
        nonce = os.urandom(16)
        self._login_nonce = nonce
        self._prp_tx(PRP_OPT_LOGIN_REQ, tx_flag=False, data=nonce, prio=True)

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
        self._prp_tx(PRP_OPT_LOGIN_RESP, tx_flag=True, data=h, prio=True)

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
        self._prp_tx(PRP_OPT_LOGIN_RESP, tx_flag=False, data=data, prio=True)

    def _rx_cmd_login_ack(self, payload: bytes):
        if self._is_ack(payload):
            logger.info(f"PRP: Login accepted !! UID: {self._uid}")
        else:
            self._set_remote_auth(False)  # oder direkt False setzen
            logger.warning(f"PRP: Login denied !! UID: {self._uid}")

    # =============================
    # ====== Logout Stuff
    def cmd_logout(self):
        """ Client sendet Logout """
        if not self._is_handshake():
            return
        self._add_pending_remote_states_cfg(PRP_OPT_LOGOUT, {'login_ok': False})
        self._prp_tx(PRP_OPT_LOGOUT, tx_flag=True, data=b'', prio=True)

    def _rx_cmd_logout(self):
        """ Server bestätigt Logout """
        print('Received Logout CMD')
        self._set_auth(False)
        self._prp_tx(PRP_OPT_LOGOUT, tx_flag=False, data=b'', prio=True)

    def _rx_cmd_logout_response(self):
        """ Client empfängt Logout bestätigung """
        print("LOGOUT erfolgreich!")
        self._set_auth(False)

    #####################################
    # Helper
    def _check_version(self):
        cli     = self._get_cli()
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

    def _has_own_state_changed(self, state_update_cfg: dict, state_key: str):
        # Checkt eingehende state updates nach Änderungen
        if state_key not in state_update_cfg:
            return False
        if state_update_cfg[state_key] == self._get_own_state(state_key):
            return False
        return True

    #####################################
    # Lokale State I/O
    # === self._own_states I/O
    def get_own_states(self):
        return dict(self._own_states)

    def set_own_state(self, state_key: str, value):
        # Opt: by Grok-AI
        if state_key not in self._own_states:
            logger.error(f"PRP State-Tab KeyError: Unbekannter Key '{state_key}'")
            return False

        current_value = self._get_own_state(state_key)
        current_type  = type(current_value)

        # Spezielle Typprüfung für Listen
        if current_type is list:
            if not isinstance(value, (list, tuple)):
                logger.error(
                    f"PRP State-Tab ValueError: Key '{state_key}' erwartet list oder tuple, bekam {type(value)}")
                return False
        # Spezielle Prüfung für batch_mode
        elif state_key == 'batch_mode':
            if value not in ('auto', 'on', 'off'):
                logger.error(f"PRP State-Tab ValueError: batch_mode muss 'auto', 'on' oder 'off' sein, nicht '{value}'")
                return False
        # Normale Typprüfung
        elif not isinstance(value, current_type):
            logger.error(f"PRP State-Tab ValueError: Key '{state_key}' erwartet {current_type}, bekam {type(value)}")
            logger.error(f"  Wert: {value}")
            return False

        # Private States loggen (aber erlauben, da lokal)
        if self._is_private_state(state_key):
            logger.warning(f"Lokaler Zugriff auf privaten State '{state_key}' = {value}")

        self._set_own_state(state_key, value)
        logger.debug(f"PRP State updated: {state_key} = {value}")
        return True

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
        if not isinstance(state_cfg, dict):
            logger.error("PRP: update_own_states: Eingabe muss ein Dictionary sein!")
            return False

        if not state_cfg:
            logger.debug("PRP: update_own_states: Leeres Update-Dict – nichts zu tun.")
            return True

        # Schritt 1: Alle Updates vorab validieren (ohne zu schreiben)
        validated_updates = {}
        for key, value in state_cfg.items():
            if key not in self._own_states:
                logger.error(f"PRP: update_own_states: Unbekannter State-Key '{key}'")
                return False

            current_value = self._get_own_state(key)
            current_type = type(current_value)

            # --- Typprüfung ---
            if current_type is list:
                if not isinstance(value, (list, tuple)):
                    logger.error(f"PRP: update_own_states: Key '{key}' erwartet list/tuple, bekam {type(value)}")
                    return False
            elif key == 'batch_mode':
                if value not in ('auto', 'on', 'off'):
                    logger.error(
                        f"PRP: update_own_states: batch_mode ungültiger Wert '{value}' (erlaubt: auto, on, off)")
                    return False
            elif not isinstance(value, current_type):
                logger.error(f"PRP: update_own_states: Key '{key}' erwartet {current_type}, bekam {type(value)}")
                return False

            # --- Wertplausibilität (optional erweitern) ---
            if key == 'rem_mon_port':
                if not (0 <= value <= 19):  # Ports typischerweise 0–19
                    logger.error(f"PRP: update_own_states: rem_mon_port außerhalb gültigem Bereich (0-19): {value}")
                    return False
            elif key == 'batch_wait':
                if not (1 <= value <= 3600):  # 1 Sekunde bis 1 Stunde sinnvoll
                    logger.warning(f"PRP: update_own_states: batch_wait ungewöhnlicher Wert: {value}s")

            # --- Private States nur loggen (nicht blockieren, da lokal) ---
            if self._is_private_state(key):
                logger.warning(f"PRP: Lokaler Update privater State '{key}' = {value}")

            validated_updates[key] = value

        # Schritt 2: Alle validierten Updates auf einmal anwenden
        for key, value in validated_updates.items():
            self._set_own_state(key, value)
            logger.debug(f"PRP State updated: {key} = {value}")

        logger.info(f"PRP update_own_states: Erfolgreich {len(validated_updates)} States aktualisiert.")
        return True

    # === self._remote_states I/O
    def get_rem_states(self):
        return self._get_remote_states()

    def get_rem_state_by_key(self, state_key: str):
        if not state_key in self._remote_states:
            return None
        return self._get_remote_state(state_key)

    #####################################
    # GUI I/O
    # == Handshake
    def _gui_resp_handshake(self):
        # == GUI Response
        gui = self._get_gui()
        if not hasattr(gui, 'init_popt_remote'):
            return
        gui.init_popt_remote(self._uid)

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
        if self._last_pack_meta is None:
            return None

        len_payload, len_compressed = self._last_pack_meta
        compression_ratio = round((len_payload / len_compressed) * 100)

        return f"PRP ▲ Compressed({compression_ratio}%) - {len_compressed}/{len_payload} Bytes"

    def _send_cli_esc_recv_status(self):
        """
        RX.
        Gibt den Status eines unvollständigen CLI-ESC-Frames zurück, falls vorhanden.
        """
        if self._next_pack_meta is None and self._comp_pack_meta is None:
            return  # Kein unvollständiges Frame oder Header unvollständig

        # == Paket ist noch im Empfang (Restbuffer)
        if self._next_pack_meta is not None:
            opt_id, payload_len = self._next_pack_meta
            # == Nur für CLI-ESC (OPT 62, TX-Flag)
            if opt_id != PRP_OPT_ESC_CLI:
                return

            # == Berechne Fortschritt
            total_bytes = 7 + payload_len  # Flag(2) + OPT(1) + LEN(2) + Payload + CRC(2)
            received_bytes = len(self._rest_buffer)

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
        if self._comp_pack_meta is not None:
            opt_id, prp_payload_len, payload_len = self._comp_pack_meta
            if opt_id != PRP_OPT_ESC_CLI:
                return
            # Optional: Kompressionsrate berechnen (wenn möglich)
            try:
                comp_ratio = f"{round(payload_len / prp_payload_len * 100)}"
            except Exception as ex:
                null = ex
                comp_ratio = "?"
            bar = '#' * 10
            status_msg = f"PRP ▼ [{bar}](100%) - Compressed({comp_ratio}%) - {prp_payload_len}/{payload_len} Bytes"
            self._send_cli_esc_status_to_QSO(status_msg, tx=False)

            self._comp_pack_meta = None
            return

        # === Mehr als total_bytes → sollte nie passieren, aber sicherheitshalber ===
        return

    @property
    def is_handshake(self):
        return self._is_handshake()

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
        if self._next_pack_meta is None:
            return

        opt_id, payload_len = self._next_pack_meta
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
    def _get_cli(self):
        if not hasattr(self._connection, 'cli'):
            return None
        return self._connection.cli

    # == Handshake
    def init_prp_handshake(self, remote_identy):
        """ Bekommt Station Identy Objekt von CLI """
        # == Keine PoPT Station TODO Liste von Erlaubten Stationen
        if not 'PoPT' in remote_identy.software:
            logger.debug("PRP: No PRP Station. No Handshake needed.")
            return
        # == Kann Gegenstation Handshake?
        if version_tuple(remote_identy.version) < version_tuple(PRP_VER_RESTR_HANDSHAKE):
            logger.warning("PRP: Version der Gegenstation ist inkompatibel. Handshake möglich !")
            logger.warning(f"PRP: Ver Gegenstation: {remote_identy.version}")
            return

        # == Remote Station Identy speichern (wenn Vorhanden)
        self._set_remote_identy(remote_identy)
        # == Eigenen Station Identy speichern (wenn Vorhanden)
        #self._set_own_identy(own_identy)
        # == Sende Handshake nur bei PoPT Sysop Stationen
        self.send_cmd_20(short_format=False)
        # == Sende Response an GUI
        self._gui_resp_handshake()

    def _get_own_stat_identy(self):
        """ Holt eigens Stat Identy Obj von CLI """
        cli = self._get_cli()
        if not hasattr(cli, 'get_own_stat_identy'):
            logger.error(f"PRP: Attribute Error: _get_own_stat_identy")
            return None
        return cli.get_own_stat_identy()

    # == CLI Abort
    def cli_abort(self):
        if not self._is_handshake():
            return False

        # == Prüfe ob CLI-ESC Pakte im TX-Buffer sind
        if not self._connection.is_prp_opt_id_in_tx_buff(PRP_OPT_ESC_CLI):
            return False
        # == Sende ABORT-RESP Frame
        self._rx_cmd_21()
        return True


