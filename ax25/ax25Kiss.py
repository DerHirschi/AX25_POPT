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
b'\xc0 \x9a\x88b\xa8\x8a\xa6\xe0\x88\x9ad\xa6\x82\xaea?\x94\x83\xc0'
Data:
....

STOP-END:
b'\xff'     <- END KISS-MODE
b'\x00'     <- END KISS-MODE

"""
from cfg.constant import TNC_KISS_CMD, TNC_KISS_CMD_END
from cfg.logger_config import logger

#############################
KISS_TXD  = b'\xC0\x01'
KISS_PERS = b'\xC0\x02'
KISS_SLOT = b'\xC0\x03'
KISS_TAIL = b'\xC0\x04'
KISS_DUPL = b'\xC0\x05'
#
DATA_FRAME  = b'\x00'   # Channel 0
SMACK_FRAME = b'\x80'  # SMACK Channel 0
# ESC & END Flags
FEND  = b'\xC0'
FESC  = b'\xDB'
TFEND = b'\xDC'
TFESC = b'\xDD'
# TNC-EMU / RX-CMDs
TNC_EMU_DC1_CMD         = b'\x11'      # <- DC1 (prevents XOFF lockup)
TNC_EMU_CAN_CMD         = b'\x18'      # <- CAN (clears out the garbage)
TNC_EMU_ESC_CMD         = b'\x1b'      # <- ESC (command mode)
TNC_EMU_KISS_CMD        = b'@K\r'      # <- change to KISS-MODE
TNC_EMU_KISS_END_CMD    = b'\xff\x00'  # <- ends KISS-MODE
TNC_EMU_KISS_END_CMD_03 = b'\xff\x03'  # <- ends KISS-MODE ???


class Kiss(object):
    def __init__(self, port_cfg: dict):
        self.is_enabled = port_cfg.get('parm_kiss_is_on', True)
        self._is_tnc_emu = False
        self._is_tnc_emu_esc = False
        self._is_tnc_emu_kiss = False
        # CFG Flags
        self._START_TNC_DEFAULT = port_cfg.get('parm_kiss_init_cmd', TNC_KISS_CMD)  # TNC2 KISS MODE   b'\x1b@K'
        self._END_TNC_DEFAULT = port_cfg.get('parm_kiss_end_cmd', TNC_KISS_CMD_END)  # TNC2 KISS MODE   b'\x1b@K'
        # SET TNC-Parameter
        self._txd_frame = FEND + KISS_TXD + bytes.fromhex(hex(port_cfg.get('parm_kiss_TXD', 35))[2:].zfill(2)) + FEND
        self._pers_frame = FEND + KISS_PERS + bytes.fromhex(hex(port_cfg.get('parm_kiss_Pers', 160))[2:].zfill(2)) + FEND
        self._slot_frame = FEND + KISS_SLOT + bytes.fromhex(hex(port_cfg.get('parm_kiss_Slot', 30))[2:].zfill(2)) + FEND
        self._tail_frame = FEND + KISS_TAIL + bytes.fromhex(hex(port_cfg.get('parm_kiss_Tail', 15))[2:].zfill(2)) + FEND
        self._duplex_frame = FEND + KISS_DUPL + bytes.fromhex(str(port_cfg.get('parm_kiss_F_Duplex', 0)).zfill(2)) + FEND
        # KISS Data Frame CH 0
        self._kiss_data_frame = lambda inp: FEND + DATA_FRAME + inp + FEND
        # Linux ax25Kernel-DEV Data Frame CH 0
        self._ax25kernel_kiss_data_frame = lambda inp: DATA_FRAME + inp
        # "FEND is sent as FESC, TFEND"  /  0xC0 is sent as 0xDB 0xDC
        self._FESC_TFEND = b''.join([FESC, TFEND])
        # "FESC is sent as FESC, TFESC"  /  0xDB is sent as 0xDB 0xDD
        self._FESC_TFESC = b''.join([FESC, TFESC])

    def set_all_parameter(self):
        return b''.join([
            self._txd_frame,
            self._pers_frame,
            self._slot_frame,
            self._tail_frame,
            self._duplex_frame,
        ])

    def set_all_parameter_ax25kernel(self):
        return [
            self._txd_frame[1:-1],
            self._pers_frame[1:-1],
            self._slot_frame[1:-1],
            self._tail_frame[1:-1],
            self._duplex_frame[1:-1],
        ]

    ######################################################################
    def unknown_kiss_frame(self, inp: bytes):
        if not self.is_enabled:
            return inp
        if inp.startswith(FEND + DATA_FRAME):
            return False
        if inp.startswith(FEND + SMACK_FRAME):
            return False
        if inp.startswith(FEND + SMACK_FRAME) and inp.endswith(FEND):
            logger.warning(f"Kiss: SMACK-Frame > {inp}")
            try:
                logger.warning(f"Kiss: SMACK-Frame HEX> {inp.hex()}")
            except SyntaxError:
                pass
            return True
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
        if any((inp.startswith(TNC_EMU_KISS_END_CMD), inp.startswith(TNC_EMU_KISS_END_CMD_03))):
            logger.info(f"Kiss: TNC-CMD received (TNC-EMU) KISS-MODE-END> {inp}")
            self._is_tnc_emu = True
            self._is_tnc_emu_esc = False
            self._is_tnc_emu_kiss = False
            return True
        if inp.startswith(TNC_EMU_KISS_CMD):
            logger.info(f"Kiss: TNC-CMD received (TNC-EMU) KISS-MODE-START> {inp}")
            if not self._is_tnc_emu_esc:
                logger.warning(f"Kiss: TNC-CMD received (TNC-EMU) KISS-MODE-START missing TNC-ESC-CMD> {inp}")
            self._is_tnc_emu = True
            self._is_tnc_emu_esc = False
            self._is_tnc_emu_kiss = True
            return True
        if inp.startswith(FEND + DATA_FRAME + FEND):
            logger.warning(f"Kiss: Empty KISS Frame > {inp}")
            return True
        if any((
                inp.startswith(KISS_TXD),
                inp.startswith(KISS_PERS),
                inp.startswith(KISS_SLOT),
                inp.startswith(KISS_TAIL),
                inp.startswith(KISS_DUPL),
        )) and inp.endswith(FEND):
            if not self._is_tnc_emu:
                logger.warning(f"Kiss: TNC-CMD received (TNC-EMU) but not in TNC-EMU-MODE> {inp}")
            if not all((self._is_tnc_emu, self._is_tnc_emu_kiss)):
                logger.warning(f"Kiss: TNC-CMD received (TNC-EMU) but not in KISS-MODE> {inp}")
            logger.info(f"Kiss: TNC-CMD received (TNC-EMU) > {inp}")
            try:
                logger.info(f"Kiss: TNC-CMD received (TNC-EMU) > {inp[2]}")
            except (SyntaxError, IndexError):
                pass
            return True
        if inp.startswith(FEND) and inp.endswith(FEND) and len(inp) > 2:
            logger.warning(f"Kiss: TNC KISS Frames ? > {inp}")
            return True
        return False

    #############################################################
    #
    def de_kiss(self, inp: bytes):
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
        # if len(inp) < 15:
        if len(inp) < 3:
            return None
        if not inp.endswith(FEND):
            return None
        if not inp.startswith(FEND + DATA_FRAME):
            return None
        return inp[2:-1].replace(
            self._FESC_TFESC,
            FESC
        ).replace(
            self._FESC_TFEND,
            FEND
        )

    def de_kiss_ax25kernel(self, inp: bytes):
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
        # if len(inp) < 15:
        if len(inp) < 2:
            return None
        if not inp.startswith(DATA_FRAME):
            return None
        # return inp[1:]
        return inp[1:].replace(
            self._FESC_TFESC,
            FESC
        ).replace(
            self._FESC_TFEND,
            FEND
        )


    def kiss(self, inp: bytes):
        """
        Code from: https://github.com/ampledata/kiss
        Recover special codes, per KISS spec.
        "If the FESC_TFESC or FESC_TFEND escaped codes appear in the data received,
        they need to be recovered to the original codes. The FESC_TFESC code is
        replaced by FESC code and FESC_TFEND is replaced by FEND code."
        - http://en.wikipedia.org/wiki/KISS_(TNC)#Description
        """
        if self.is_enabled:
            return self._kiss_data_frame(
                inp.replace(
                    FESC,
                    self._FESC_TFESC
                ).replace(
                    FEND,
                    self._FESC_TFEND
                )
            )
        return inp

    def kiss_ax25kernel(self, inp: bytes):
        """
        Code from: https://github.com/ampledata/kiss
        Recover special codes, per KISS spec.
        "If the FESC_TFESC or FESC_TFEND escaped codes appear in the data received,
        they need to be recovered to the original codes. The FESC_TFESC code is
        replaced by FESC code and FESC_TFEND is replaced by FEND code."
        - http://en.wikipedia.org/wiki/KISS_(TNC)#Description
        """
        if self.is_enabled:
            return self._ax25kernel_kiss_data_frame(
                inp.replace(
                    FESC,
                    self._FESC_TFESC
                ).replace(
                    FEND,
                    self._FESC_TFEND
                )
            )
        return inp


    #############################################################################
    def device_kiss_end(self):
        # return b''.join([self.FEND, self.RETURN, self.FEND])
        return self._END_TNC_DEFAULT

    def device_kiss_start_1(self):
        return self._START_TNC_DEFAULT
