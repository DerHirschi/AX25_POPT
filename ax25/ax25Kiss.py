"""
Idea from:
https://github.com/ampledata/kiss
Doc:
http://www.symek.com/pdf/extra.pdf

TODO: MultiKiss ( Direwolf Channels / TNC PORTS)
CH0 Data: \xc0\x00 <AX25-Frame> \x0c\xc0'
CH1 Data: \xc0\x10 <AX25-Frame> \x0c\xc0'
CH2 Data: \xc0\x20 <AX25-Frame> \x0c\xc0'
SMACK:
CH0 Data: \xc0\x80 <AX25-Frame>'  FEND 0x80 DATA DATA ... DATA CRCLOW CRCHIGH FEND
CH1 Data: \xc0\x90 <AX25-Frame> '
...
NL5VKL-2

---------------------------------------------
b'\x11'     <- DC1 (prevents XOFF lockup)
b'\x18'     <- CAN (clears out the garbage)
b'\x1b'     <- ESC (command mode)
b'@'        <- change to KISS-MODE
b'K'        <- change to KISS-MODE
b'\r'       <-
---------------------------------------------
AMICOM:
b'\xc0\x01\x19\xc0'
b'\xc0\x02@\xc0'
b'\xc0\x03\n\xc0'
b'\xc0\x04\x03\xc0'
b'\xc0\x05\x00\xc0'

b'\xc0\x01\x19\xc0'
b'\xc0\x02\xc8\xc0'
b'\xc0\x03\n\xc0'
b'\xc0\x04\x03\xc0'
b'\xc0\x05\x00\xc0'

b'\xc0\x01#\xc0'
b'\xc0\x02\xc8\xc0'
b'\xc0\x03\n\xc0'
b'\xc0\x04\x03\xc0'
b'\xc0\x05\x00\xc0'

b'\xc0\x01#\xc0'
b'\xc0\x02\xc8\xc0'
b'\xc0\x03\x1e\xc0'
b'\xc0\x04\x03\xc0'
b'\xc0\x05\x00\xc0'

---------------------------------------------
STOP-TFPCX:

Garbage fm DOS-BOX-X when starting
b'\xff'     <- END KISS-MODE
b'\x00'     <- END KISS-MODE

b'\xff'
b'\x00'

b'\xff'
b'\x00'

STOP-Start/TFPCX:
b'\xff'
b'\x03'     <- ?????

b'\xc0\x01\x19\xc0'
b'\xc0\x02 \xc0'
b'\xc0\x03\n\xc0'
b'\xc0\x05\x00\xc0'

b'\xc0\x01#\xc0'
b'\xc0\x03\n\xc0'
b'\xc0\x02\xbe\xc0'

SMACK-Frame:
b'\xc0\x80\x9a\x88b\xa8\x8a\xa6\xe0\x88\x9ad\xa6\x82\xaea?\xa3\x17\xc0'
Unknown-KISS:
b'\xc0     \x9a\x88b\xa8\x8a\xa6\xe0\x88\x9ad\xa6\x82\xaea?\x94\x83\xc0'
KISS:
....

STOP-END:
b'\xff'     <- END KISS-MODE
b'\x00'     <- END KISS-MODE

"""
from ax25.ax25dec_enc import bytearray2hexstr
from cfg.constant import TNC_KISS_CMD, TNC_KISS_CMD_END
from cfg.logger_config import logger
from ax25 import crc_x25
from fnc.crc_fnc import crc_smack

#############################
KISS_TXD  = b'\xC0\x01'
KISS_PERS = b'\xC0\x02'
KISS_SLOT = b'\xC0\x03'
KISS_TAIL = b'\xC0\x04'
KISS_DUPL = b'\xC0\x05'
# KISS_DUPL = b'\xC0\x0F' # CRC-Mode ???
##############################################
# KISS
DATA_FRAME_0  = b'\x00'     # Channel 0
# DATA_FRAME_1  = b'\x10'     # Channel 1
# DATA_FRAME_2  = b'\x20'     # Channel 2
# DATA_FRAME_3  = b'\x30'     # Channel 3
# DATA_FRAME_4  = b'\x40'     # Channel 4
# DATA_FRAME_5  = b'\x50'     # Channel 5
# DATA_FRAME_6  = b'\x60'     # Channel 6
# DATA_FRAME_7  = b'\x70'     # Channel 7
##############################################
# SMACK
SMACK_FRAME_0 = b'\x80'       # SMACK Channel 0
# SMACK_FRAME_1 = b'\x90'       # SMACK Channel 1
# SMACK_FRAME_2 = b'\xa0'       # SMACK Channel 2
# SMACK_FRAME_3 = b'\xb0'       # SMACK Channel 3
# SMACK_FRAME_4 = b'\xc0'       # SMACK Channel 4
# SMACK_FRAME_5 = b'\xd0'       # SMACK Channel 5
# SMACK_FRAME_6 = b'\xe0'       # SMACK Channel 6
# SMACK_FRAME_7 = b'\xf0'       # SMACK Channel 7
##############################################
# TNC-EMU / RX-CMDs
TNC_EMU_DC1_CMD         = b'\x11'           # <- DC1 (prevents XOFF lockup)
TNC_EMU_CAN_CMD         = b'\x18'           # <- CAN (clears out the garbage)
TNC_EMU_ESC_CMD         = b'\x1b'           # <- ESC (command mode)
TNC_EMU_KISS_CMD        = b'@K\r'           # <- change to KISS-MODE
TNC_EMU_KISS_CMD_03     = b'\xff\x03'       # <- change to KISS-MODE ???
TNC_EMU_KISS_END_CMD    = b'\xff\x00'       # <- ends KISS-MODE ???
TNC_EMU_KISS_END_CMD_C0 = b'\xc0\xff\xc0'   # <- ends KISS-MODE
##############################################
# ESC & END Flags
FEND  = b'\xC0'
FESC  = b'\xDB'
TFEND = b'\xDC'
TFESC = b'\xDD'

FESC_TFEND = b''.join([FESC, TFEND])    # "FEND is sent as FESC, TFEND"  /  0xC0 is sent as 0xDB 0xDC
FESC_TFESC = b''.join([FESC, TFESC])    # "FESC is sent as FESC, TFESC"  /  0xDB is sent as 0xDB 0xDD
##############################################
# KISS Data Frame CH 0
KISS_DATA_FRAME_0            = lambda inp: FEND + DATA_FRAME_0 + inp + FEND
##############################################
# Linux ax25Kernel-DEV Data Frame CH 0
AX25KERNEL_DATA_FRAME_0     = lambda inp: DATA_FRAME_0 + inp

class Kiss(object):
    def __init__(self, port_cfg: dict):
        self.is_enabled         = port_cfg.get('parm_kiss_is_on', True)
        self.set_kiss_param     = port_cfg.get('parm_set_kiss_param', True)
        self._port_id           = port_cfg.get('parm_PortNr', -1)
        # TNC Modes (KISS(+x-25 crc), SMACK)
        self._tnc_ch            = 0
        self._fcs_mode          = port_cfg.get('parm_kiss_fcs_mode', 'off') # 'on', 'off', 'auto'
        self._can_smack_ext     = False     # Cfg. SMACK-EXT lookup (buggy)
        #
        self._no_crc_count      = 0
        self._is_smack          = False
        self._is_smack_ext      = False     # SMACK-EXTENDED (The Firmware 2.42)
        # TNC EMU Ctrl
        self._is_tnc_emu        = False
        self._is_tnc_emu_esc    = False
        self._is_tnc_emu_kiss   = False
        # CFG Flags
        self._START_TNC_KISS = port_cfg.get('parm_kiss_init_cmd', TNC_KISS_CMD)
        self._END_TNC_KISS   = port_cfg.get('parm_kiss_end_cmd', TNC_KISS_CMD_END)
        # SET TNC-Parameter
        self._txd_frame    = FEND + KISS_TXD +  bytes.fromhex(hex(port_cfg.get('parm_kiss_TXD', 35))[2:].zfill(2)) + FEND
        self._pers_frame   = FEND + KISS_PERS + bytes.fromhex(hex(port_cfg.get('parm_kiss_Pers', 160))[2:].zfill(2)) + FEND
        self._slot_frame   = FEND + KISS_SLOT + bytes.fromhex(hex(port_cfg.get('parm_kiss_Slot', 30))[2:].zfill(2)) + FEND
        self._tail_frame   = FEND + KISS_TAIL + bytes.fromhex(hex(port_cfg.get('parm_kiss_Tail', 15))[2:].zfill(2)) + FEND
        self._duplex_frame = FEND + KISS_DUPL + bytes.fromhex(str(port_cfg.get('parm_kiss_F_Duplex', 0)).zfill(2)) + FEND

        # ██████████████████████████████████████████████████████████████
        # ███ LOGGING BEI INIT █████████████████████████████████████████
        # ██████████████████████████████████████████████████████████████
        logger.info("═" * 60)
        logger.info(f"KISS INITIALISIERT - Port {self._port_id}")
        logger.info(f"  Enabled:          {self.is_enabled}")
        #logger.info(f"  Multi-Channel:    {self.multi_channel}")
        logger.info(f"  FCS Mode:         {self._fcs_mode.upper()} {'← DEFAULT FÜR DIREWOLF!' if port_cfg.get('parm_kiss_fcs_mode', 'auto') == 'off' else ''}")
        logger.info(f"  Set KISS Params:  {self.set_kiss_param}")
        logger.info(f"  Start-CMD: {self._START_TNC_KISS}")
        logger.info(f"  END-CMD:   {self._END_TNC_KISS}")
        logger.info(f"  TXD:       {port_cfg.get('parm_kiss_TXD', 35)}")
        logger.info(f"  Pers:      {port_cfg.get('parm_kiss_Pers', 160)}")
        logger.info(f"  Slot:      {port_cfg.get('parm_kiss_Slot', 30)}")
        logger.info(f"  Tail:      {port_cfg.get('parm_kiss_Tail', 15)}")
        logger.info(f"  Duplex:    {port_cfg.get('parm_kiss_F_Duplex', 0)}")
        logger.info("═" * 60)

    def set_all_parameter(self):
        if not self.set_kiss_param:
            logger.info(f"Kiss: Set TNC-Parameter disabled !")
            return b''
        return b''.join([
            self._txd_frame,
            self._pers_frame,
            self._slot_frame,
            self._tail_frame,
            self._duplex_frame,
        ])

    def set_all_parameter_ax25kernel(self):
        if not self.set_kiss_param:
            logger.info(f"Kiss: Set TNC-Parameter disabled !")
            return []
        return [
            self._txd_frame[1:-1],
            self._pers_frame[1:-1],
            self._slot_frame[1:-1],
            self._tail_frame[1:-1],
            self._duplex_frame[1:-1],
        ]

    ######################################################################
    def _dec_tnc_emu_parameter(self, inp: bytearray):
        if not self._is_tnc_emu:
            logger.warning(f"Kiss: TNC-CMD received (TNC-EMU) but not in TNC-EMU-MODE> {inp}")
        if not all((self._is_tnc_emu, self._is_tnc_emu_kiss)):
            logger.warning(f"Kiss: TNC-CMD received (TNC-EMU) but not in KISS-MODE> {inp}")

        if inp.startswith(KISS_TXD):
            logger.info(f"Kiss: TNC-CMD received (TNC-EMU) TXD > {inp}")
            try:
                logger.info(f"Kiss: TNC-CMD received (TNC-EMU) TXD: {inp[2]}")
            except (SyntaxError, IndexError):
                pass
        elif inp.startswith(KISS_PERS):
            logger.info(f"Kiss: TNC-CMD received (TNC-EMU) PERS > {inp}")
            try:
                logger.info(f"Kiss: TNC-CMD received (TNC-EMU) PERS: {inp[2]}")
            except (SyntaxError, IndexError):
                pass
        elif inp.startswith(KISS_SLOT):
            logger.info(f"Kiss: TNC-CMD received (TNC-EMU) SLOT > {inp}")
            try:
                logger.info(f"Kiss: TNC-CMD received (TNC-EMU) SLOT: {inp[2]}")
            except (SyntaxError, IndexError):
                pass
        elif inp.startswith(KISS_TAIL):
            logger.info(f"Kiss: TNC-CMD received (TNC-EMU) TAIL > {inp}")
            try:
                logger.info(f"Kiss: TNC-CMD received (TNC-EMU) TAIL: {inp[2]}")
            except (SyntaxError, IndexError):
                pass
        elif inp.startswith(KISS_DUPL):
            logger.info(f"Kiss: TNC-CMD received (TNC-EMU) F-Duplex > {inp}")
            try:
                logger.info(f"Kiss: TNC-CMD received (TNC-EMU) F-Duplex: {inp[2]}")
            except (SyntaxError, IndexError):
                pass

    ######################################################################
    def unknown_kiss_frame(self, inp: bytearray):
        if not self.is_enabled:
            return inp
        if inp.startswith(FEND + DATA_FRAME_0):
            return False
        if not inp.startswith(FEND) and len(inp) > 3:
            logger.warning(f"Kiss: NO KISS Frame > {inp}")
            return True
        if inp.startswith(TNC_EMU_DC1_CMD):
            logger.info(f"Kiss: TNC-CMD received (TNC-EMU) DC1 (prevents XOFF lockup)> {inp}")
            self._is_tnc_emu = True
            self._is_tnc_emu_esc = False
            self._is_tnc_emu_kiss = False
            return True
        if inp.startswith(TNC_EMU_CAN_CMD):
            logger.info(f"Kiss: TNC-CMD received (TNC-EMU) CAN (clears out the garbage)> {inp}")
            self._is_tnc_emu = True
            self._is_tnc_emu_esc = False
            self._is_tnc_emu_kiss = False
            return True
        if inp.startswith(TNC_EMU_ESC_CMD):
            logger.info(f"Kiss: TNC-CMD received (TNC-EMU) ESC (command mode)> {inp}")
            self._is_tnc_emu = True
            self._is_tnc_emu_esc = True
            self._is_tnc_emu_kiss = False
            return True
        if any((inp.startswith(TNC_EMU_KISS_END_CMD), inp.startswith(TNC_EMU_KISS_END_CMD_C0))):
            logger.info(f"Kiss: TNC-CMD received (TNC-EMU) KISS-MODE-END> {inp}")
            self._is_tnc_emu = True
            self._is_tnc_emu_esc = False
            self._is_tnc_emu_kiss = False
            return True
        if any((inp.startswith(TNC_EMU_KISS_CMD), inp.startswith(TNC_EMU_KISS_CMD_03))):
            logger.info(f"Kiss: TNC-CMD received (TNC-EMU) KISS-MODE-START> {inp}")
            if not self._is_tnc_emu_esc and not inp.startswith(TNC_EMU_KISS_CMD_03):
                logger.warning(f"Kiss: TNC-CMD received (TNC-EMU) KISS-MODE-START missing TNC-ESC-CMD> {inp}")
            self._is_tnc_emu = True
            self._is_tnc_emu_esc = False
            self._is_tnc_emu_kiss = True
            return True
        if inp.startswith(FEND + DATA_FRAME_0 + FEND):
            logger.warning(f"Kiss: Empty KISS Frame > {inp}")
            return True
        if any((
                inp.startswith(KISS_TXD),
                inp.startswith(KISS_PERS),
                inp.startswith(KISS_SLOT),
                inp.startswith(KISS_TAIL),
                inp.startswith(KISS_DUPL),
        )) and inp.endswith(FEND):
            self._dec_tnc_emu_parameter(inp)
            return True
        if inp.startswith(FEND) and inp.endswith(FEND) and len(inp) > 2:
            # if inp.startswith(FEND + DATA_FRAME_1):
            if int(inp[1] / 16) in range(1, 8):
                logger.warning(f"Kiss: Received Frame for TNC-CH {int(inp[1] / 16)}. Multi-Channel TNCs are not supported yet.")
                logger.warning(f"Kiss: {inp}")
                # TODO
                self._tnc_ch = int(inp[1] / 16)
                return True
            # if inp.startswith(FEND + SMACK_FRAME_0):
            if int(inp[1] / 16) in range(8, 16):
                logger.warning(f"Kiss: Received Frame for TNC-SMACK-CH {inp[1] - 128}. Multi-Channel TNCs are not supported yet.")
                #logger.warning(f"Kiss: SMACK is not supported yet.")
                logger.warning(f"Kiss: {inp}")
                self._is_smack = True
                self._fcs_mode = 'on'
                return True
            logger.warning(f"Kiss: TNC KISS Frames ? > {inp}")
            return True
        return False

    #############################################################
    # CRC
    @staticmethod
    def _get_crc(de_kissed_frame: bytearray):
        crc = de_kissed_frame[-2:]
        crc = int(bytearray2hexstr(crc[::-1]), 16)
        pack = de_kissed_frame[:-2]
        calc_crc = crc_x25(pack)
        return pack, crc, calc_crc

    @staticmethod
    def _get_smack_crc(de_kissed_frame: bytearray):
        if len(de_kissed_frame) < 2:
            return de_kissed_frame, 0, 0

        crc_received = int.from_bytes(de_kissed_frame[-2:], 'little')
        pack = de_kissed_frame[:-2]
        calc_crc = crc_smack(pack)
        return pack, crc_received, calc_crc

    #############################################################
    # KISS it
    def de_kiss(self, inp: bytearray):
        """
        Code from: https://github.com/ampledata/kiss
        Escape special codes, per KISS spec.
        "If the FEND or FESC codes appear in the data to be transferred, they
        need to be escaped. The FEND code is then sent as FESC, TFEND and the
        FESC is then sent as FESC, TFESC."
        - http://en.wikipedia.org/wiki/KISS_(TNC)#Description
        """
        if not self.is_enabled:
            return inp
        if len(inp) < 3:
            return None
        if not inp.endswith(FEND):
            return None
        if not inp.startswith(FEND):
            return None
        if inp[1] / 16 not in range(0, 16):
            # No KISS-Data Frames 00, 10, 20, ...
            logger.warning(f"De-Kiss: No KISS/SMACK-Data Frames: {int(inp[1] / 16)} ")
            logger.debug(f"> {inp}")
            logger.debug(f"> {inp.hex()}")
            return None

        if self._is_smack_ext:
            # SMACK-EXT
            self._tnc_ch = int(inp[1] / 16)
            org_pack     = inp[1:-1]
            return self._do_smack_ext_crc_in_packet(org_pack)

        if inp[1] / 16 in range(0, 8):
            # KISS & SMACK-EXT
            #logger.debug(f"De-Kiss: Receiving packet on TNC Channel: {int(inp[1] / 16)} ")
            #logger.debug(f"> {inp}")
            #logger.debug(f"> {inp.hex()}")
            # TODO
            self._tnc_ch = int(inp[1] / 16)
            org_pack     = inp[1:-1]
            ###################################
            # SMACK-EXT Erkennung (vor Escaping!) ---
            if self._can_smack_ext:
                if len(org_pack) >= 3:
                    seq_byte = org_pack[-3]
                    crc_low  = org_pack[-2]
                    data     = org_pack[:-3]

                    calc_full = crc_x25(data) ^ 0xFFFF
                    calc_low  = calc_full & 0xFF

                    if calc_low == crc_low:
                        logger.info(f"SMACK-EXT ERKANNT! SEQ=0x{seq_byte:02x} | Port {self._port_id}")
                        self._is_smack_ext = True
                        self._fcs_mode = 'on'
                        self._no_crc_count = 0
                        return data[1:]

                if self._is_smack_ext:
                    return None
            ###################################
            # Escape KISS
            org_pack = org_pack.replace(
                FESC_TFESC,
                FESC
            ).replace(
                FESC_TFEND,
                FEND
            )
            return self._do_kiss_crc_in_packet(org_pack)

        if int(inp[1] / 16) in range(8, 16):
            # SMACK
            logger.warning(f"De-Kiss: Receiving SMACK packet on TNC Channel: {int(inp[1] / 16)} ")
            # logger.warning(f"Kiss: SMACK is not supported yet.")
            logger.warning(f"Kiss: {inp}")
            self._tnc_ch   = int(inp[1] / 16)
            self._is_smack = True
            self._fcs_mode = 'on'
            org_pack = inp[1:-1]
            return self._do_smack_crc_in_packet(org_pack)
        return None

    def de_kiss_ax25kernel(self, inp: bytearray):
        """
        Code from: https://github.com/ampledata/kiss
        Escape special codes, per KISS spec.
        "If the FEND or FESC codes appear in the data to be transferred, they
        need to be escaped. The FEND code is then sent as FESC, TFEND and the
        FESC is then sent as FESC, TFESC."
        - http://en.wikipedia.org/wiki/KISS_(TNC)#Description
        """
        if not self.is_enabled:
            return inp
        if len(inp) < 2:
            return None
        if inp[0] / 16 not in range(0, 8):
            return None
        if int(inp[0] / 16) in range(1, 8):
            logger.warning(f"De-Kiss ax25Kernel: Receiving packet on TNC Channel: {int(inp[0] / 16)} ")
        ###################################
        # Escape
        org_pack = inp[1:].replace(
            FESC_TFESC,
            FESC
        ).replace(
            FESC_TFEND,
            FEND
        )
        return self._do_kiss_crc_in_packet(org_pack)

    def _do_kiss_crc_in_packet(self, org_pack: bytearray):
        if self._fcs_mode == 'off':
            return org_pack[1:]

        pack, recv_crc, calc_crc = self._get_crc(org_pack)
        if recv_crc == calc_crc:
            if self._fcs_mode == 'auto':
                logger.info(f"KISS CRC OK → using KISS | Port {self._port_id}")
                self._fcs_mode = 'on'
            return pack[1:]

        if self._fcs_mode == 'auto':
            logger.info("KISS CRC failed → no valid mode")
            self._no_crc_count += 1
            if self._no_crc_count > 3:
                self._fcs_mode = 'off'
            return org_pack[1:]

        logger.warning(f"KISS CRC failed | Port {self._port_id}")
        return org_pack[1:]

    def _do_smack_crc_in_packet(self, org_pack: bytearray):
        # SMACK
        pack, crc, calc_crc = self._get_smack_crc(org_pack)
        if crc == calc_crc:
            return pack[1:]

        logger.debug(f"SMACK CRC-Check Port {self._port_id}")
        logger.debug(f"  Pack-CRC ({crc}) != Clac-CRC ({calc_crc})")
        logger.debug(f"  Pack:     {org_pack}")
        logger.debug(f"  Pack-Hex: {org_pack.hex()}")
        return None

    @staticmethod
    def _do_smack_ext_crc_in_packet(org_pack: bytearray):
        if len(org_pack) < 3:
            return None

        seq_byte = org_pack[-3]
        crc_low = org_pack[-2]
        data = org_pack[:-3]

        calc_full = crc_x25(data) ^ 0xFFFF
        calc_low = calc_full & 0xFF

        if calc_low == crc_low:
            logger.debug(f"SMACK-EXT CRC OK | SEQ=0x{seq_byte:02x}")
            return data[1:]
        else:
            logger.debug(f"SMACK-EXT CRC failed | recv=0x{crc_low:02x} != calc=0x{calc_low:02x}")
            return None

    ######################################################
    def kiss(self, inp: bytearray):
        if not self.is_enabled:
            return inp

        if self._fcs_mode == 'on':
            if self._is_smack:
                calc_crc = crc_smack(inp)  # ← SMACK CRC!
                inp = inp + calc_crc.to_bytes(2, 'little')  # ← Little-Endian!
            else:
                calc_crc = crc_x25(inp)
                inp = inp + calc_crc

        # SMACK braucht KEIN Escaping!
        if self._is_smack:
            return FEND + SMACK_FRAME_0 + inp + FEND
        else:
            return KISS_DATA_FRAME_0(
                inp.replace(FESC, FESC_TFESC).replace(FEND, FESC_TFEND)
            )

    def kiss_ax25kernel(self, inp: bytearray):
        """
        Code from: https://github.com/ampledata/kiss
        Recover special codes, per KISS spec.
        "If the FESC_TFESC or FESC_TFEND escaped codes appear in the data received,
        they need to be recovered to the original codes. The FESC_TFESC code is
        replaced by FESC code and FESC_TFEND is replaced by FEND code."
        - http://en.wikipedia.org/wiki/KISS_(TNC)#Description
        """
        if not self.is_enabled:
            return inp

        if self._fcs_mode == 'on':
            calc_crc = crc_x25(inp)
            inp = inp + calc_crc

        return AX25KERNEL_DATA_FRAME_0(
            inp.replace(
                FESC,
                FESC_TFESC
            ).replace(
                FEND,
                FESC_TFEND
            )
        )


    #############################################################################
    def device_kiss_end(self):
        if not self.set_kiss_param:
            logger.info(f"Kiss: KISS-END: Set TNC-Parameter disabled !")
            return b''
        # return b''.join([self.FEND, self.RETURN, self.FEND])
        return self._END_TNC_KISS

    def device_kiss_start(self):
        if not self.set_kiss_param:
            logger.info(f"Kiss: KISS-Start: Set TNC-Parameter disabled !")
            return b''
        return self._START_TNC_KISS
    #############################################################################
    def get_tnc_emu_status(self):
        return self._is_tnc_emu, self._is_tnc_emu_kiss


