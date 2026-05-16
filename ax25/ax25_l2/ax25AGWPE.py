from cfg.logger_config import logger


class AGWPEHandler:
    def __init__(self, port_cfg):
        self.protocol_name = 'AGWPE'
        self._agwpe_channel = 0
        self.is_enabled     = True
        self.set_param      = True
        call_from = 'PoPT-V2'[:9].ljust(10, '\x00')  # null-terminated + padded
        self._call_from = call_from.encode()[:10]
        self._app_name  = self._call_from  # App Name

    def _R_frame(self):
        # return b''
        header = bytearray(36)  # 36 Header + 36 Data = 72 Bytes
        header[0] = self._agwpe_channel
        header[4] = 0x52  # 'R'
        header[8:18] = self._app_name
        header[18:28] = self._call_from  # User Call
        header[28:32] = (0).to_bytes(4, 'little')  # DataLen = 36
        header[32:36] = b'\x00\x00\x00\x00'  # Reserved

        return bytes(header)

    def _G_frame(self):
        """AGWPE 'G' Frame: Request Capabilities (Ports, Channels, etc.)"""
        header = bytearray(36)
        header[0] = self._agwpe_channel
        header[4] = 0x47  # 'G'
        header[8:18] = self._app_name
        header[18:28] = self._call_from
        header[28:32] = (0).to_bytes(4, 'little')  # DataLen = 0
        header[32:36] = b'\x00\x00\x00\x00'
        return bytes(header)

    def _k_frame(self):
        """AGWPE 'k' Frame: Register Callsign (Login ohne Passwort)"""
        header = bytearray(36)
        header[0] = self._agwpe_channel
        header[4] = 0x6B  # 'k'
        header[8:18] = self._app_name
        header[18:28] = self._call_from
        header[28:32] = (0).to_bytes(4, 'little')  # DataLen = 0
        header[32:36] = b'\x00\x00\x00\x00'
        return bytes(header)

    """
    def _P_frame(self):
        # return b''
        header = bytearray(36)  # 36 Header + 36 Data = 72 Bytes
        header[0] = self._agwpe_channel
        header[4] = 0x50  # 'P'
        header[8:18] = self._app_name
        header[18:28] = self._call_from  # User Call
        header[28:32] = (510).to_bytes(4, 'little')  # DataLen = 36
        header[32:36] = b'\x00\x00\x00\x00'  # Reserved

        # --- 36 Bytes Data (beliebig, aber oft Version + Info) ---
        user_name =  'test1'.ljust(255, '\x00').encode('ASCII', 'ignore')
        passw     =  'test'.ljust(255, '\x00').encode('ASCII', 'ignore')

        logger.debug(f"AGWPE LOGIN: Channel={self._agwpe_channel}, App='PoPT', Call='{self._call_from.decode().rstrip(chr(0))}'")
        return bytes(header + user_name + passw)
    """

    def _K_frame(self, ax25_frame: bytes):
        """ Sending 'K' Frames with raw ax25-frame """
        data_kind   = 0x4B  # Data Frame
        data_len    = len(ax25_frame)
        data_len += 1

        # --- 36-Byte Header ---
        header          = bytearray(36)
        header[0]       = self._agwpe_channel
        header[4]       = 0x4B  # 'K'
        header[8:18]    = self._app_name  # App Name
        header[18:28]   = self._call_from  # User Call
        header[28:32]   = data_len.to_bytes(4, 'little')  # DataLen = 36
        header[32:36]   = b'\x00\x00\x00\x00'  # Reserved

        packet = header + b'\x00' + ax25_frame
        logger.debug(f"AGWPE TX: Port={self._agwpe_channel}, Kind=0x{data_kind}, Len={data_len}")

        return bytes(packet)

    def encode_tnc(self, ax25_frame: bytes):
        return self._K_frame(ax25_frame)

    #######################################################
    # Decoding
    def decode_tnc(self, raw: bytes):
        if len(raw) < 36:
            return None

        data_kind = raw[4]

        if data_kind == 0x4B:    # 'K'
            return self._dec_K_frame(raw)
        elif data_kind == 0x52:  # 'R'
            return self._dec_R_frame(raw)
        elif data_kind == 0x47:  # 'G'
            return self._dec_G_frame(raw)
        elif data_kind == 0x6B:  # 'k'
            return self._dec_k_frame(raw)
        else:
            return None

    @staticmethod
    def _dec_K_frame(raw: bytes):
        port            = raw[0]
        pid             = raw[6]
        call_from       = raw[8:18].rstrip(b'\x00').decode(errors='ignore')
        call_to         = raw[18:28].rstrip(b'\x00').decode(errors='ignore')
        data_len        = int.from_bytes(raw[28:32], 'little')
        reserved        = raw[32:36]
        expected_len    = 36 + data_len
        if len(raw) != expected_len:
            logger.warning(f"AGWPE RX K: Length mismatch: got {len(raw)}, expected {expected_len}")
            return None

        if reserved != b'\x00\x00\x00\x00':
            logger.debug(f"AGWPE RX K: Non-zero reserved field: {reserved.hex()}")

        # --- AX.25 Data extrahieren ---
        ax25_data = raw[36:36 + data_len]
        tnc_ch = ax25_data[0]
        # recv_crc = raw[-2:]

        # --- CRC prüfen ---
        # calc_crc = crc_x25(ax25_data)
        # if recv_crc != calc_crc:
        #    logger.warning(f"AGWPE RX: CRC failed! recv={recv_crc}, calc={calc_crc}")
        #    return None

        # --- Erfolgreich! ---
        logger.debug(
            f"AGWPE RX K: {call_from} → {call_to} | Port {port} | Len {data_len} | PID 0x{pid:02X} | tnc_ch: {tnc_ch}")
        return bytearray(ax25_data[1:])

    @staticmethod
    def _dec_R_frame(raw: bytes):
        """

        """
        try:
            # --- Header parsen ---
            port         = raw[0]
            data_kind    = raw[4]           # muss 0x52 ('R') sein
            pid          = raw[6]
            call_from    = raw[8:18].rstrip(b'\x00').decode('ascii', errors='ignore')
            call_to      = raw[18:28].rstrip(b'\x00').decode('ascii', errors='ignore')
            data_len     = int.from_bytes(raw[28:32], 'little')
            reserved     = raw[32:36]

            # --- Länge prüfen ---
            expected_len = 36 + data_len
            if len(raw) != expected_len:
                return None

            # --- Daten extrahieren ---
            data = raw[36:36 + data_len]

            # --- Version parsen (falls vorhanden) ---
            version = None
            if data_len >= 4:
                version = int.from_bytes(data[0:4], 'little')

            # --- Nur geparste Daten loggen ---
            logger.info(f"AGWPE R-Frame: Port={port}")
            logger.info(f"  DataKind: 0x{data_kind:02X} ('R')")
            logger.info(f"  PID:      0x{pid:02X}")
            logger.info(f"  CallFrom: '{call_from}'")
            logger.info(f"  CallTo:   '{call_to}'")
            logger.info(f"  DataLen:  {data_len}")
            logger.info(f"  Reserved: {reserved.hex()}")
            if version is not None:
                logger.info(f"  Version:  {version} (0x{version:04X})")
            if data_len > 4:
                logger.info(f"  Extra:    {data[4:].hex()}")

            parsed_data = {
                'port': port,
                'data_kind': data_kind,
                'pid': pid,
                'call_from': call_from,
                'call_to': call_to,
                'data_len': data_len,
                'reserved': reserved,
                'version': version,
                'extra_data': data[4:] if data_len > 4 else b''
            }
            return None
        except Exception as e:
            logger.error(f"AGWPE R-Frame decode error: {e}")
            return None

    @staticmethod
    def _dec_G_frame(raw: bytes):
        """Decoder für AGWPE 'G' Response (Capabilities)"""
        try:
            port         = raw[0]
            data_kind    = raw[4]      # 0x47
            pid          = raw[6]
            call_from    = raw[8:18].rstrip(b'\x00').decode('ascii', errors='ignore')
            call_to      = raw[18:28].rstrip(b'\x00').decode('ascii', errors='ignore')
            data_len     = int.from_bytes(raw[28:32], 'little')
            reserved     = raw[32:36]

            if len(raw) != 36 + data_len:
                return None

            data = raw[36:36 + data_len]
            capabilities = data.decode('ascii', errors='ignore').rstrip('\x00')

            # Nur geparste Daten loggen
            logger.info(f"AGWPE G-Frame: Port={port}")
            logger.info(f"  DataKind:  0x{data_kind:02X} ('G')")
            logger.info(f"  PID:       0x{pid:02X}")
            logger.info(f"  CallFrom:  '{call_from}'")
            logger.info(f"  CallTo:    '{call_to}'")
            logger.info(f"  DataLen:   {data_len}")
            logger.info(f"  Reserved:  {reserved.hex()}")
            logger.info(f"  Ports:     {capabilities}")

            decoded_data =  {
                'port': port,
                'data_kind': data_kind,
                'pid': pid,
                'call_from': call_from,
                'call_to': call_to,
                'data_len': data_len,
                'reserved': reserved,
                'capabilities': capabilities
            }
            return None

        except Exception as e:
            logger.error(f"AGWPE G-Frame decode error: {e}")
            return None

    @staticmethod
    def _dec_k_frame(raw: bytes):
        """Decoder für AGWPE 'k' Response (Register Callsign) – meist leer"""
        try:
            port         = raw[0]
            data_kind    = raw[4]      # 0x6B
            pid          = raw[6]
            call_from    = raw[8:18].rstrip(b'\x00').decode('ascii', errors='ignore')
            call_to      = raw[18:28].rstrip(b'\x00').decode('ascii', errors='ignore')
            data_len     = int.from_bytes(raw[28:32], 'little')
            reserved     = raw[32:36]

            if len(raw) != 36 + data_len:
                return None

            data = raw[36:36 + data_len] if data_len > 0 else b''

            logger.info(f"AGWPE k-Frame: Port={port}")
            logger.info(f"  DataKind:  0x{data_kind:02X} ('k')")
            logger.info(f"  PID:       0x{pid:02X}")
            logger.info(f"  CallFrom:  '{call_from}'")
            logger.info(f"  CallTo:    '{call_to}'")
            logger.info(f"  DataLen:   {data_len}")
            logger.info(f"  Reserved:  {reserved.hex()}")
            if data_len > 0:
                logger.info(f"  Data:      {data.decode('ascii', errors='ignore')}")

            decoded_data = {
                'port': port,
                'data_kind': data_kind,
                'pid': pid,
                'call_from': call_from,
                'call_to': call_to,
                'data_len': data_len,
                'reserved': reserved,
                'response_data': data.decode('ascii', errors='ignore') if data_len > 0 else ''
            }
            return None

        except Exception as e:
            logger.error(f"AGWPE k-Frame decode error: {e}")
            return None

    #####################################################
    @staticmethod
    def start_cmd():
        return b''

    @staticmethod
    def end_cmd():
        return b''

    def device_start(self):
        return [self._R_frame(), self._G_frame(), self._k_frame()]

    @staticmethod
    def set_kiss_param():
        return b''

    @staticmethod
    def set_all_parameter():
        return b''

    @staticmethod
    def device_end():
        return b''
