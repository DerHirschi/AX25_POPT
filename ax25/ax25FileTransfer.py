import time
from cfg.logger_config import logger
import datetime

from cfg.constant import FT_MODES, FT_RX_HEADERS, CFG_ft_downloads
from ax25.Yapp import Yapp
from fnc.crc_fnc import get_crc
from fnc.os_fnc import path_exists
from fnc.str_fnc import calculate_time_remaining, calculate_percentage, get_file_timestamp


def ft_rx_header_lookup(data: b'', last_pack: b''):
    data = last_pack + data
    lines = data.split(b'\r')
    for line in lines:
        for mode in FT_RX_HEADERS:
            if line.startswith(mode):
                ret = {
                    FT_RX_HEADERS[0]: is_autobin(line[line.index(mode):]),
                    FT_RX_HEADERS[1]: is_yapp_SI(line[line.index(mode):]),  # SI
                    # FT_RX_HEADERS[2]: is_yapp_RI(data[data.index(FT_RX_HEADERS[2]):]),  # RI - Server Mode
                }[mode]
                if ret:
                    return ret

    return False


def is_autobin(header):
    # if header[-1:] != b'\r':
    #     return False
    parts = header.split(b'#')
    if not parts:
        return False
    parts = parts[1:]
    if len(parts) < 2:
        return False
    if parts[0] != b'BIN':
        return False
    if not parts[1].isdigit():
        return False
    if len(parts) == 2:
        # BIN MODE
        new_ft_obj = FileTransport(
            filename='',
            protocol=FT_MODES[1],
            # connection=None,
            tx_wait=0,
            direction='RX'
        )
        # return parts[1], 0, 0, '', False
        new_ft_obj.raw_data_len = int(parts[1])

        return new_ft_obj
    if len(parts) != 5:
        return False
    if parts[2][:1] != b'|':
        return False

    if not parts[2][1:].isdigit():
        return False

    if parts[3][:1] != b'$':
        return False
    """
    if not parts[3][1:].isdigit():
        print(f"not parts[3][1:].isdigit(): {parts}")
        return False
    """
    size = int(parts[1])
    crc = int(parts[2][1:])
    # datetime_hex = parts[3][1:]
    filename = parts[4].decode('ASCII', 'ignore')

    new_ft_obj = FileTransport(
        filename=filename,
        protocol=FT_MODES[2],
        # connection=None,
        tx_wait=0,
        direction='RX'
    )
    new_ft_obj.raw_data_len = size
    new_ft_obj.raw_data_crc = crc
    # return size, crc, datetime_hex, filename, True
    return new_ft_obj


def check_autobin(header: bytes):
    # if header[-1:] != b'\r':
    #     return False
    # parts = header[1:-1].split(b'#')
    header = header.replace(b'\r', b'')
    parts = header.split(b'#')
    if not parts:
        return False
    parts = parts[1:]
    if len(parts) < 2:
        return False
    if parts[0] != b'BIN':
        return False
    # len
    if not parts[1].isdigit():
        return False
    if len(parts) == 2:
        # BIN MODE
        return True
    elif len(parts) != 5:
        return False
    if parts[2][:1] != b'|':
        return False
    if not parts[2][1:].isdigit():
        return False
    if parts[3][:1] != b'$':
        return False
    """
    if not parts[3][1:].isdigit():
        return False
    """
    return True


def is_yapp_SI(header):
    if header == FT_RX_HEADERS[1]:
        new_ft_obj = FileTransport(
            filename='',
            protocol=FT_MODES[3],
            # connection=None,
            tx_wait=0,
            direction='RX'
        )
        return new_ft_obj
    return False


def is_yapp_RI(header):
    if header == FT_RX_HEADERS[2]:
        new_ft_obj = FileTransport(
            filename='',
            protocol=FT_MODES[3],
            # connection=None,
            tx_wait=0,
            direction='RX'
        )
        return new_ft_obj
    return False


class FileTransport(object):
    def __init__(self,
                 filename: str = '',
                 protocol: str = '',
                 connection=None,
                 tx_wait: int = 0,
                 direction: str = 'TX'
                 ):
        self.dir = direction
        self.param_filename = filename
        self.param_protocol = protocol
        self.param_wait = int(tx_wait)
        self.param_PacLen = 128
        self.param_MaxFrame = 3
        self.connection = connection

        """
        if self.connection is not None:
            self.param_PacLen = self.connection.parm_PacLen
            self.param_MaxFrame = self.connection.parm_MaxFrame
        """

        self.raw_data = b''
        self.raw_data_len = 0
        self.raw_data_crc = 0
        self.ft_tx_buf = b''
        self.ft_rx_buf = b''
        self.e = False
        self.done = False
        self.abort = False
        self.pause = False
        self.can_rnr = False
        self.last_tx = 0
        self.time_start = 0
        self.tmp_param_wait = 0
        """ DEBUG """
        #self.debug_raw_data = b''
        #self.debug_last_frames = []
        #self.debug_trigger = False
        #self.debug_run = False

        self.prot_dict = {
            FT_MODES[0]: TextMODE,
            FT_MODES[1]: BinMODE,
            FT_MODES[2]: AutoBinMODE,
            FT_MODES[3]: YappMODE,
            FT_MODES[4]: YappCMODE,
        }
        self.class_protocol = DefaultMODE(self)
        if self.param_protocol in self.prot_dict.keys():
            self.class_protocol = self.prot_dict[self.param_protocol](self)

        if self.dir == 'TX':
            self.process_file()
            self.class_protocol.init_TX()
        else:
            self.e = self.class_protocol.init_RX()
            # self.debug_process_file()

    """
    def debug_process_file(self):
        try:
            with open('DEV_STUFF/Sally.exe', 'rb') as file:
                self.debug_raw_data = file.read()

        except PermissionError:
            print("DEBUG FILE INIT ERROR")
        self.debug_run = True

    """
    def process_file(self):
        try:
            with open(self.param_filename, 'rb') as file:
                buf = file.read()
                self.raw_data = buf
                self.raw_data_len = len(buf)
                self.raw_data_crc = get_crc(buf)
        except PermissionError:
            self.e = True
        if not self.raw_data:
            self.e = True

    def ft_init(self):
        # print()
        if not self.raw_data:
            self.e = True
            return False
        if self.connection is None:
            self.e = True
            return False
        if self.param_protocol in self.prot_dict.keys():
            self.param_PacLen = self.connection.parm_PacLen
            self.param_MaxFrame = self.connection.parm_MaxFrame
            self.class_protocol = self.prot_dict[self.param_protocol](self)
            self.class_protocol.init_TX()
            self.e = False
            return True
        self.e = True
        return False

    def ft_init_rx(self):
        pass

    def ft_can_start(self):
        if self.connection is None:
            return False
        if self.pause:
            return False
        if not self.connection.get_tx_buff_len():
            return True
        return False

    def ft_can_stop(self):
        if not self.connection.get_tx_buff_len():
            return True
        return False

    def ft_flush_buff(self):
        self.ft_rx_buf = b''
        self.ft_tx_buf = b''
        if self.connection is not None:
            self.connection.clear_tx_buff()

    def ft_recover_buff(self):
        self.ft_tx_buf = self.connection.get_tx_buff() + self.ft_tx_buf
        self.connection.clear_tx_buff()

    def ft_mode_wait_for_end(self):
        if self.ft_can_stop():
            self.ft_end()

    def ft_start(self):
        if not self.time_start:
            self.time_start = time.time()

    def ft_end(self):
        # self.debug_find_missing_data()
        self.done = True

    def ft_abort(self):
        """ To trigger from the outside (GUI) """
        if self.pause:
            self.ft_pause()
        self.param_wait = 0
        self.abort = True
        if self.time_start:
            self.class_protocol.exec_abort()
        else:
            self.ft_end()

    def ft_pause(self):
        """ To trigger from the outside (GUI) """
        if self.class_protocol.parm_can_pause:
            if not self.pause:
                self.pause = True
                self.class_protocol.exec_pause()
                return True
            self.pause = False
        return False

    def ft_set_wait_timer(self):
        if self.param_wait:
            self.last_tx = self.param_wait + time.time()

    def ft_can_send(self):
        if self.pause:
            return False
        if self.param_wait:
            if self.last_tx < time.time():
                self.ft_set_wait_timer()
            else:
                return False
        if not self.connection.get_tx_buff_len() \
                and not self.connection.tx_buf_2send \
                and not self.connection.tx_buf_unACK:
            return True
        return False

    def ft_crone(self):
        if self.done:
            if self.class_protocol is not None:
                del self.class_protocol
                self.class_protocol = None
            return False
        if self.pause:
            return True
        if not self.e:
            # Set RNR for RECV
            if self.dir != 'TX':
                self.ft_rnr()
            return self.class_protocol.crone_mode()
        return False

    def ft_rnr(self):
        if self.connection is not None:
            if not self.param_wait:
                if self.connection.is_RNR:
                    self.connection.unset_RNR()
                return
            if self.connection.is_RNR:
                if self.last_tx < time.time():
                    self.connection.unset_RNR()
                    self.can_rnr = False
                return

            if self.can_rnr and self.last_tx > time.time():
                self.connection.set_RNR()
                self.ft_set_wait_timer()
                return

        """
        if self.connection is not None:
            if not self.param_wait:
                if self.connection.is_RNR:
                    self.connection.unset_RNR()
            else:

                if not self.connection.is_RNR:
                    if self.can_rnr:
                        self.connection.set_RNR()
                        print("Conn Set RNR")
                        self.ft_set_wait_timer()
                else:
                    if self.last_tx < time.time():
                        self.connection.unset_RNR()
                        self.can_rnr = False
        """


    def ft_switch_rnr(self):
        if self.connection is not None:
            self.can_rnr = False
            if self.pause:
                if not self.connection.is_RNR:
                    self.connection.set_RNR()
                    self.tmp_param_wait = self.param_wait
                    self.param_wait = 0

            else:
                if self.connection.is_RNR:
                    self.connection.unset_RNR()
                    self.param_wait = self.tmp_param_wait
                    self.last_tx = time.time()

    def ft_rx(self, data: b''):
        self.ft_rx_buf += data
        return True
        # TODO Pause State (Auswertung der Pakete)
        # if self.pause:
        #     return True  # let CLI disabled
        # if self.debug_run:
        #     self.debug_input(data)

    """
    def debug_input(self, data):
        if self.debug_run:
            self.debug_last_frames.append(data)
            while len(self.debug_last_frames) > 3:
                del self.debug_last_frames[0]
            if self.debug_trigger:
                out = "\n++++ DEB INPUT ++++\n"
                c = 0
                for el in self.debug_last_frames:
                    out += f"Index: {c} > raw: {el}\n"
                    out += f"Index: {c} > hex: {el.hex()}\n\n"
                    c += 1
                out += "++++ DEB INPUT Ende++++\n\n"
                print(out)
                logger.debug(out)

    def debug_find_missing_data(self):
        if self.debug_run:
            c = 0
            for el in self.raw_data:
                if el != self.debug_raw_data[c]:
                    self.debug_trigger = True
                    out   = "\n++++ DEB TRIGGER ++++\n"
                    out += f"Index: {c}\n"
                    out += "RAW[c - 100:]\n"
                    out += f"raw: {self.raw_data[min(c - 100, c - len(self.raw_data)):]}\n\n"
                    out += f"debug: {self.debug_raw_data[min(c - 100, c - len(self.debug_raw_data)):len(self.raw_data)]}\n\n"
                    out += "HEX[c - 100:]\n"
                    out += f"raw.hex: {self.raw_data[min(c - 100, c - len(self.raw_data)):].hex()}\n\n"
                    out += f"debug.hex  : {self.debug_raw_data[min(c - 100, c - len(self.debug_raw_data)):len(self.raw_data)].hex()}\n\n"
                    out += "\n++++ DEB TRIGGER ENDE ++++\n\n"
                    print(out)
                    logger.debug(out)
                c += 1
    """

    def ft_tx(self, data):
        self.connection.send_data(data, file_trans=True)

    def get_ft_infos(self):
        time_spend = (time.time() - self.time_start)
        time_spend = datetime.timedelta(seconds=time_spend)
        if self.dir == 'TX':
            data_in_buf = len(self.ft_tx_buf) + self.connection.get_tx_buff_len()
            data_sendet = self.raw_data_len - data_in_buf
            time_remaining, baud_rate, percentage_completion = calculate_time_remaining(time_spend,
                                                                                        self.raw_data_len,
                                                                                        data_sendet)

            return percentage_completion, self.raw_data_len, data_sendet, time_spend, time_remaining, baud_rate

        time_remaining, baud_rate, percentage_completion = calculate_time_remaining(time_spend,
                                                                                    self.raw_data_len,
                                                                                    len(self.raw_data))
        return percentage_completion, self.raw_data_len, len(self.raw_data), time_spend, time_remaining, baud_rate

    def get_ft_info_percentage(self):
        if self.dir == 'TX':
            data_in_buf = len(self.ft_tx_buf) + self.connection.get_tx_buff_len()
            data_sendet = self.raw_data_len - data_in_buf
            return round(calculate_percentage(self.raw_data_len, data_sendet), 1)
        else:
            return round(calculate_percentage(self.raw_data_len, len(self.raw_data)), 1)

    def get_ft_info_status(self):
        yapp_state = ''
        if self.class_protocol.yapp is not None:
            yapp_state = f" - {self.class_protocol.yapp.state}"
        if self.abort or self.class_protocol.abort:
            return 'ABORT' + yapp_state
        if self.e or self.class_protocol.e:
            return 'ERROR' + yapp_state
        if self.done:
            return 'DONE' + yapp_state
        if self.pause:
            return 'PAUSE' + yapp_state
        if not self.class_protocol.state:
            return 'WAIT' + yapp_state
        if not self.time_start:
            return 'INIT' + yapp_state
        return self.dir + yapp_state

    def get_ft_active_status(self):
        """ FT-Manager Buttons de/activate """
        if self.abort or self.class_protocol.abort:
            return False
        if self.e or self.class_protocol.e:
            return False
        if self.done:
            return False
        # if not self.time_start:
        #     return False
        return True

    def get_ft_can_pause(self):
        return self.class_protocol.parm_can_pause


class DefaultMODE(object):
    def __init__(self, ft_root):
        self.ft_root: FileTransport = ft_root
        self.connection = ft_root.connection
        self.ft_root.ft_tx_buf = bytes(self.ft_root.raw_data)
        self.filename = self.ft_root.param_filename.split('/')[-1]
        self.state_tab = {}
        self.state = 0
        self.header = b''
        self.e = True  # No Prot set
        self.start = False
        self.abort = False
        self.parm_can_pause = False
        self.yapp = None
        self.file = None

    def init_TX(self):
        pass

    def init_RX(self):
        return False

    def open_file(self):
        self.e = True
        if not self.filename:
            self.filename = get_file_timestamp() + '.dat'
        if not path_exists(CFG_ft_downloads + self.filename):
            try:
                self.file = open(CFG_ft_downloads + self.filename, 'wb')
                self.e = False
                return True
            except (PermissionError, ValueError, FileNotFoundError):
                return False
        return False

    def close_file(self):
        if self.file is not None:
            self.file.close()
            self.file = None

    def crone_mode(self):
        if not self.e:
            if self.state in self.state_tab:
                self.state_tab[self.state]()
                # self.ft_root.ft_rx_buf = b''
                return True
        self.e = True
        return False

    def send_data(self, data):
        self.ft_root.ft_tx(data=data)

    def exec_abort(self):
        pass

    def exec_pause(self):
        pass

    def start_ft(self):
        self.ft_root.ft_start()
        self.state_tab[self.state]()


class TextMODE(DefaultMODE):
    def init_TX(self):
        self.state_tab = {
            0: self.mode_wait_for_start,
            1: self.mode_s1,  # W/O Wait / direct to tx_buff
            2: self.mode_s2,  # With wait handling
            3: self.ft_root.ft_mode_wait_for_end,
        }
        self.state = 0
        self.e = False
        self.parm_can_pause = True

    def mode_wait_for_start(self):
        self.start = True
        if self.ft_root.ft_can_start():
            if self.ft_root.param_wait:
                self.state = 2
            else:
                self.state = 1
            self.start_ft()

    def mode_s1(self):
        self.send_data(bytes(self.ft_root.ft_tx_buf))
        self.ft_root.ft_tx_buf = b''
        self.state = 3
        return True

    def mode_s2(self):
        """ :returns doesn't matter """
        if not self.ft_root.param_wait:
            self.state = 1
        if self.ft_root.ft_can_send():
            tmp_len = self.ft_root.param_PacLen * self.ft_root.param_MaxFrame
            if len(self.ft_root.ft_tx_buf) < tmp_len:
                tmp = self.ft_root.ft_tx_buf
                tmp_len = len(tmp)
                # self.ft_root.done = True
                self.state = 3
            else:
                tmp = self.ft_root.ft_tx_buf[:tmp_len]
            self.send_data(tmp)
            self.ft_root.ft_tx_buf = self.ft_root.ft_tx_buf[tmp_len:]
            return True
        return True

    def exec_abort(self):
        self.ft_root.ft_flush_buff()
        self.send_data(b'\r#ABORT#\r')
        self.abort = True
        self.state = 3

    def exec_pause(self):
        # if self.state == 3:
        self.ft_root.ft_recover_buff()
        self.state = 0


class AutoBinMODE(DefaultMODE):
    def init_TX(self):
        # self.ft_root.ft_tx_buf = bytes(self.ft_root.data)
        self.state_tab = {
            0: self.mode_wait_for_free_tx_buf,
            1: self.mode_init,
            2: self.mode_init_resp,
            3: self.mode_tx_data,
            4: self.mode_tx_data_steps,
            5: self.mode_tx_end_resp,
            6: self.mode_pause,
            9: self.ft_root.ft_mode_wait_for_end,
        }
        """ Simple Mode .. There seems another Mode but i can't find any specs. """
        # self.header = f'\r#BIN#{self.ft_root.raw_data_len}\r'.encode('ASCII')
        pos = '0' * 8  # Don't know how to decode. Maybe it's a Timestamp but results don't match.
        self.filename = self.filename.replace(' ', '_').upper()
        self.header = f"#BIN#{self.ft_root.raw_data_len}#|{int(self.ft_root.raw_data_crc)}#${pos}#{self.filename}\r".encode(
            'ASCII')
        self.state = 0
        self.e = False
        self.parm_can_pause = True

    def init_RX(self):
        self.state_tab = {
            0: self._mode_init_rx,
            1: self._mode_rx_data,
            8: self.exec_abort,
            9: self.ft_root.ft_mode_wait_for_end,
        }
        self.state = 0
        self.e = False
        self.parm_can_pause = True
        self.open_file()
        if self.e:

            self.state = 8
            self.e = False
            # self.exec_abort()
        return self.e

    def mode_wait_for_free_tx_buf(self):
        self.start = True
        if self.ft_root.ft_can_start():
            self.state = 1

    def mode_init(self):
        self.send_data(self.header)
        self.state = 2

    def _mode_init_rx(self):
        if self.ft_root.ft_rx_buf:
            # print(f'_mode_init_rx - {self.ft_root.ft_rx_buf}')
            if check_autobin(self.ft_root.ft_rx_buf):
                self.start = True
                self.ft_root.ft_rx_buf = b''
                self.state = 1
                self.send_data(b'#OK#\r')
                self.start_ft()
            else:
                self.e = True
                self.state = 9

    def _mode_rx_data(self):
        if not self.check_abort():
            if self.ft_root.ft_rx_buf:
                self.ft_root.can_rnr = True
                length = min(
                    self.ft_root.raw_data_len - len(self.ft_root.raw_data),
                    len(self.ft_root.ft_rx_buf))
                self.file.write(self.ft_root.ft_rx_buf[:length])
                self.ft_root.raw_data += self.ft_root.ft_rx_buf[:length]
                self.ft_root.ft_rx_buf = self.ft_root.ft_rx_buf[length:]
                if len(self.ft_root.raw_data) == self.ft_root.raw_data_len:
                    """ END """
                    # self.state = 2
                    crc = get_crc(self.ft_root.raw_data)
                    # print(f"AutoBIN RX ENDE {crc}")
                    # print(f"AutoBIN RX ENDE rest: {self.ft_root.ft_rx_buf}")
                    self.file.close()
                    self.state = 9
                    self.ft_root.can_rnr = False

    def mode_init_resp(self):
        if self.ft_root.ft_rx_buf:
            lines = self.ft_root.ft_rx_buf.split(b'\r')
            self.ft_root.ft_rx_buf = b''
            lines = [x for x in lines if x != b'']
            if lines:
                if lines[-1] == b'#OK#':
                    if self.ft_root.param_wait:
                        self.state = 4
                    else:
                        self.state = 3
                    self.start_ft()
                elif b'#ABORT#' in lines:
                    self.exec_abort()

    def mode_tx_data(self):
        if not self.check_abort():
            self.send_data(bytes(self.ft_root.ft_tx_buf))
            self.ft_root.ft_tx_buf = b''
            self.state = 5
            return True

    def mode_tx_data_steps(self):
        if not self.check_abort():
            if self.ft_root.ft_can_send():
                tmp_len = self.ft_root.param_PacLen * self.ft_root.param_MaxFrame
                if len(self.ft_root.ft_tx_buf) < tmp_len:
                    tmp = self.ft_root.ft_tx_buf
                    tmp_len = len(tmp)
                    # self.ft_root.done = True
                    self.state = 5
                else:
                    tmp = self.ft_root.ft_tx_buf[:tmp_len]
                self.send_data(tmp)
                self.ft_root.ft_tx_buf = self.ft_root.ft_tx_buf[tmp_len:]

    def mode_tx_end_resp(self):
        """ END """
        self.send_data(f'\rBIN-TX OK #{int(self.ft_root.raw_data_crc)}\r\r'.encode('ASCII'))
        self.state = 9
        """
        if self.ft_root.ft_rx_buf:
            lines = self.ft_root.ft_rx_buf.split(b'\r')
            self.ft_root.ft_rx_buf = b''
            if lines[-1] == b'#OK#':
                # self.send_data(b'BIN-TX OK #25059\r')
                self.send_data(f'BIN-TX OK #{int(self.ft_root.raw_data_crc)}\r'.encode('ASCII'))
                self.state = 9
            elif b'#ABORT#' in lines:
                self.exec_abort()
        """

    def mode_pause(self):
        if self.ft_root.ft_can_start():
            if self.ft_root.param_wait:
                self.state = 4
            else:
                self.state = 3

    def check_abort(self):
        if self.ft_root.ft_rx_buf:
            lines = self.ft_root.ft_rx_buf.split(b'\r')

            if b'#ABORT#' in lines:
                self.exec_abort()
                return True
        return False

    def exec_abort(self):
        self.ft_root.ft_flush_buff()
        self.send_data(b'\r#ABORT#\r')
        self.abort = True
        self.state = 9

    def exec_pause(self):
        self.state = 6
        self.ft_root.ft_recover_buff()


class BinMODE(DefaultMODE):
    def init_TX(self):
        # self.ft_root.ft_tx_buf = bytes(self.ft_root.data)
        self.state_tab = {
            0: self.mode_wait_for_free_tx_buf,
            1: self.mode_init,
            2: self.mode_init_resp,
            3: self.mode_tx_data,
            4: self.mode_tx_data_steps,
            5: self.mode_tx_end_resp,
            6: self.mode_pause,
            9: self.ft_root.ft_mode_wait_for_end,
        }
        """ Simple Mode .. There seems another Mode but i can't find any specs. """
        # self.header = f'\r#BIN#{self.ft_root.raw_data_len}\r'.encode('ASCII')
        pos = '0' * 8  # Don't know how to decode. Maybe it's a Timestamp but results don't match.
        self.filename = self.filename.replace(' ', '_').upper()
        self.header = f"#BIN#{self.ft_root.raw_data_len}#|{int(self.ft_root.raw_data_crc)}#${pos}#{self.filename}\r".encode(
            'ASCII')
        self.state = 0
        self.e = False
        self.parm_can_pause = True

    def init_RX(self):
        self.state_tab = {
            0: self.mode_init_rx,
            1: self.mode_rx_data,
            8: self.exec_abort,
            9: self.ft_root.ft_mode_wait_for_end,
        }
        self.state = 0
        self.e = False
        self.parm_can_pause = True
        self.open_file()
        if self.e:
            self.state = 8
            self.e = False
        return self.e

    def mode_wait_for_free_tx_buf(self):
        self.start = True
        if self.ft_root.ft_can_start():
            self.state = 1

    def mode_init(self):
        self.send_data(self.header)
        # self.state = 2
        if self.ft_root.param_wait:
            self.state = 4
        else:
            self.state = 3
        self.start_ft()

    def mode_init_rx(self):
        if self.ft_root.ft_rx_buf:
            if check_autobin(self.ft_root.ft_rx_buf):
                self.start = True
                self.ft_root.ft_rx_buf = b''
                self.state = 1
                self.send_data(b'#OK#')
                self.start_ft()
            else:
                self.e = True
                self.state = 9

    def mode_rx_data(self):
        if not self.check_abort():
            if self.ft_root.ft_rx_buf:
                self.ft_root.can_rnr = True
                length = min(
                    self.ft_root.raw_data_len - len(self.ft_root.raw_data),
                    len(self.ft_root.ft_rx_buf))

                self.file.write(self.ft_root.ft_rx_buf[:length])
                self.ft_root.raw_data += self.ft_root.ft_rx_buf[:length]
                self.ft_root.ft_rx_buf = self.ft_root.ft_rx_buf[length:]
                if len(self.ft_root.raw_data) == self.ft_root.raw_data_len:
                    """ END """
                    # self.state = 2
                    crc = get_crc(self.ft_root.raw_data)
                    print(f"AutoBIN RX ENDE {self.ft_root.raw_data_crc} <> {crc}")
                    if crc == self.ft_root.raw_data_crc:
                        print(f"CRC OK")
                    print(f"AutoBIN RX ENDE rest: {self.ft_root.ft_rx_buf}")
                    self.file.close()
                    self.state = 9
                    self.ft_root.can_rnr = False

    def mode_init_resp(self):
        pass

    def mode_tx_data(self):
        if not self.check_abort():
            self.send_data(bytes(self.ft_root.ft_tx_buf))
            self.ft_root.ft_tx_buf = b''
            self.state = 5
            return True

    def mode_tx_data_steps(self):
        if not self.check_abort():
            if self.ft_root.ft_can_send():
                tmp_len = self.ft_root.param_PacLen * self.ft_root.param_MaxFrame
                if len(self.ft_root.ft_tx_buf) < tmp_len:
                    tmp = self.ft_root.ft_tx_buf
                    tmp_len = len(tmp)
                    # self.ft_root.done = True
                    self.state = 5
                else:
                    tmp = self.ft_root.ft_tx_buf[:tmp_len]
                self.send_data(tmp)
                self.ft_root.ft_tx_buf = self.ft_root.ft_tx_buf[tmp_len:]

    def mode_tx_end_resp(self):
        """ END """
        self.state = 9

    def mode_pause(self):
        if self.ft_root.ft_can_start():
            if self.ft_root.param_wait:
                self.state = 4
            else:
                self.state = 3

    def check_abort(self):
        if self.ft_root.ft_rx_buf:
            lines = self.ft_root.ft_rx_buf.split(b'\r')
            # self.ft_root.ft_rx_buf = b''
            if b'#ABORT#' in lines:
                self.exec_abort()
                return True
        return False

    def exec_abort(self):
        self.ft_root.ft_flush_buff()
        self.send_data(b'\r#ABORT#\r')
        self.abort = True
        self.state = 9

    def exec_pause(self):
        self.state = 6
        self.ft_root.ft_recover_buff()


class YappMODE(DefaultMODE):
    def init_TX(self):
        print("Yapp prot_class INIT")
        self.state_tab = {
            0: self.mode_wait_for_free_tx_buf,
            1: self.mode_init,
            2: self.mode_yapp,
            9: self.ft_root.ft_mode_wait_for_end,
        }
        self.filename = self.filename.replace(' ', '_')
        self.state = 0
        self.e = False
        self.parm_can_pause = False
        self.yapp = Yapp(self)

    def init_RX(self):
        print("Yapp prot_class INIT-RX")
        # TODO
        self.state_tab = {
            0: self.mode_wait_for_free_tx_buf,
            1: self.mode_init_RX,
            2: self.mode_yapp,
            9: self.ft_root.ft_mode_wait_for_end,
        }
        self.filename = ''
        self.state = 0
        self.e = False
        self.parm_can_pause = True
        self.yapp = Yapp(self)

    def mode_wait_for_free_tx_buf(self):
        self.start = True
        if self.ft_root.ft_can_start():
            self.state = 1

    def mode_init(self):
        # self.yapp.file_rawdata = self.ft_root.ft_tx_buf
        self.yapp.file_name = self.filename
        if self.connection is not None:
            self.yapp.param_proto_conn = True
        if self.yapp.init_tx():
            if not self.yapp.e:
                self.state = 2
                self.e = False
                self.yapp.e = self.e
                self.start_ft()
                # self.yapp.send_init_pack()
                return True
        # self.state = 9
        print("Yapp Init Error (mode_init)")
        logger.error("Yapp Init Error (mode_init)")
        self.e = True
        return False

    def mode_init_RX(self):
        if self.connection is not None:
            self.yapp.param_proto_conn = True
        if self.yapp.init_rx():
            if not self.yapp.e:
                self.state = 2
                self.e = False
                self.yapp.e = self.e
                self.start_ft()
                # self.yapp.send_init_pack()
                print("Yapp Init RX (mode_init)")
                return True
            # self.state = 9
        print("Yapp Init Error (mode_init)")
        logger.error("Yapp Init Error (mode_init)")
        self.e = True
        return False

    def mode_yapp(self):
        # print("Yapp (mode_yapp)")
        if self.yapp.Done:
            self.state = 9
            print("Yapp (mode_yapp) Done !")
            return
        if self.yapp.e:
            print("Yapp Error (mode_yapp)")
            logger.error("Yapp Error (mode_yapp)")
            self.state = 9
            return
        if self.ft_root.ft_rx_buf:
            # inp_len = len(self.ft_root.ft_rx_buf)
            tmp = bytes(self.ft_root.ft_rx_buf)
            self.ft_root.ft_rx_buf = b''
            self.yapp.yapp_rx(tmp)
            return
        else:
            # print("Yapp (mode_yapp) Cron")
            self.yapp.yapp_cron()
            return

    def write_to_file(self, data: b''):
        self.file.write(data)
        self.ft_root.raw_data += data

    def can_send(self):
        # TODO process all Yapp packets at once or just if wait_timer is triggered
        """
        if len(self.ft_root.connection.tx_buf_unACK) < self.ft_root.param_MaxFrame:
            return True
        """
        if self.yapp is not None:
            if self.yapp.state == 'SD':
                if self.ft_root.ft_can_send():
                    return True
                return False
        return True

    def send_data(self, data):
        self.ft_root.ft_tx(data=data)

    def exec_abort(self):
        self.ft_root.ft_flush_buff()
        self.yapp.exec_abort()

    def exec_pause(self):
        """ Just in RX Mode """
        self.ft_root.ft_switch_rnr()
    """
    def crone_mode(self):
        #if self.e:
        #    return False
        #if self.state != 2:
        #    return False
        #self.yapp.yapp_cron()
        #return True
        if not self.e:
            if self.state in self.state_tab:
                self.state_tab[self.state]()
                return True
        self.e = True
        return False
    """


class YappCMODE(YappMODE):
    def init_TX(self):
        print("Yapp prot_class INIT")
        self.state_tab = {
            0: self.mode_wait_for_free_tx_buf,
            1: self.mode_init,
            2: self.mode_yapp,
            9: self.ft_root.ft_mode_wait_for_end,
        }
        self.filename = self.filename.replace(' ', '_')
        self.state = 0
        self.e = False
        self.parm_can_pause = False
        self.yapp = Yapp(self)
        self.yapp.YappC = True
        self.yapp.ext_header = True

