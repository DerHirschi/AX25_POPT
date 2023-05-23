import time
import logging
import datetime

from constant import FT_MODES
from ax25.Yapp import Yapp
from fnc.crc_fnc import get_crc
from fnc.str_fnc import calculate_time_remaining, calculate_percentage

logger = logging.getLogger(__name__)


class FileTX(object):
    def __init__(self,
                 filename: str,
                 protocol: str == '',
                 connection,
                 tx_wait: int = 0,
                 ):
        self.dir = 'TX'
        self.param_filename = str(filename)
        self.param_protocol = str(protocol)
        self.param_wait = int(tx_wait)
        self.param_PacLen = connection.parm_PacLen
        self.param_MaxFrame = connection.parm_MaxFrame
        self.connection = connection

        self.prot_dict = {
            FT_MODES[0]: TextMODE_TX,
            FT_MODES[1]: BinMODE_TX,
            FT_MODES[2]: AutoBinMODE_TX,
            FT_MODES[3]: YappMODE_TX,
        }

        self.raw_data = b''
        self.raw_data_len = 0
        self.raw_data_crc = 0
        self.ft_tx_buf = b''
        self.ft_rx_buf = b''
        self.e = False
        self.done = False
        self.abort = False
        self.pause = False
        self.last_tx = 0
        self.time_start = 0

        try:
            self.process_file(self.param_filename)
        except PermissionError:
            self.e = True
        if not self.raw_data:
            self.e = True

        if self.param_protocol in self.prot_dict.keys():
            self.class_protocol = self.prot_dict[self.param_protocol](self)
            self.class_protocol.init()
        else:
            self.class_protocol = DefaultMODE_TX(self)

    def process_file(self, filename):
        with open(filename, 'rb') as file:
            buf = file.read()
            self.raw_data = buf
            self.raw_data_len = len(buf)
            self.raw_data_crc = get_crc(buf)

    def ft_init(self):
        # print()
        if not self.raw_data:
            self.e = True
            return False
        if self.param_protocol in self.prot_dict.keys():
            self.class_protocol = self.prot_dict[self.param_protocol](self)
            self.class_protocol.init()
            self.e = False
            return True
        self.e = True
        return False

    def ft_can_start(self):
        if self.pause:
            return False
        if not self.connection.tx_buf_rawData and \
                not self.connection.rx_buf_rawData:
            return True
        return False

    def ft_can_stop(self):
        if not self.connection.tx_buf_rawData:
            return True
        return False

    def ft_flush_buff(self):
        self.ft_rx_buf = b''
        self.ft_tx_buf = b''
        self.connection.tx_buf_rawData = b''

    def ft_recover_buff(self):
        self.ft_tx_buf = bytes(self.connection.tx_buf_rawData) + self.ft_tx_buf
        self.connection.tx_buf_rawData = b''

    def ft_mode_wait_for_end(self):
        if self.ft_can_stop():
            self.ft_end()

    def ft_start(self):
        if not self.time_start:
            self.time_start = time.time()

    def ft_end(self):
        self.done = True

    def ft_abort(self):
        """ To trigger from the outside (GUI) """
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
        if not self.connection.tx_buf_rawData\
                and not self.connection.tx_buf_2send\
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
            return self.class_protocol.crone_mode()

    def ft_rx(self):
        # TODO Pause State (Auswertung der Pakete)
        # self.ft_rx_buf += bytes(self.connection.rx_buf_rawData)
        if self.pause:
            return True     # let CLI disabled
        self.ft_rx_buf += bytes(self.connection.rx_buf_rawData)
        self.connection.rx_buf_rawData = b''
        return True

    def ft_tx(self, data):
        self.connection.send_data(data, file_trans=True)

    def get_ft_infos(self):
        data_in_buf = len(self.ft_tx_buf) + len(self.connection.tx_buf_rawData)
        data_sendet = self.raw_data_len - data_in_buf
        time_spend = (time.time() - self.time_start)
        time_spend = datetime.timedelta(seconds=time_spend)
        time_remaining, baud_rate, percentage_completion = calculate_time_remaining(time_spend,
                                                                                    self.raw_data_len,
                                                                                    data_sendet)

        return percentage_completion, self.raw_data_len, data_sendet, time_spend, time_remaining, baud_rate

    def get_ft_info_percentage(self):
        data_in_buf = len(self.ft_tx_buf) + len(self.connection.tx_buf_rawData)
        data_sendet = self.raw_data_len - data_in_buf
        return round(calculate_percentage(self.raw_data_len, data_sendet), 1)

    def get_ft_info_status(self):
        if self.abort or self.class_protocol.abort:
            return 'ABORT'
        if self.e or self.class_protocol.e:
            return 'ERROR'
        if self.done:
            return 'DONE'
        if self.pause:
            return 'PAUSE'
        if not self.class_protocol.state:
            return 'WAIT'
        if not self.time_start:
            return 'INIT'
        return 'TX'

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


class DefaultMODE_TX(object):
    def __init__(self, ft_root):
        self.ft_root: FileTX = ft_root
        self.connection = ft_root.connection
        self.ft_root.ft_tx_buf = bytes(self.ft_root.raw_data)
        self.filename = self.ft_root.param_filename.split('/')[-1]
        self.header = b''
        self.state_tab = {}
        self.state = 0
        self.e = True  # No Prot set
        self.start = False
        self.abort = False
        self.parm_can_pause = False
        self.yapp = None

    def init(self):
        pass

    def crone_mode(self):
        if not self.e:
            if self.state in self.state_tab:
                self.state_tab[self.state]()
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


class TextMODE_TX(DefaultMODE_TX):
    def init(self):
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
        #if self.state == 3:
        self.ft_root.ft_recover_buff()
        self.state = 0


class AutoBinMODE_TX(DefaultMODE_TX):
    def init(self):
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
        pos = '0' * 8   # Don't know how to decode. Maybe it's a Timestamp but results don't match.
        self.filename = self.filename.replace(' ', '_').upper()
        self.header = f"#BIN#{self.ft_root.raw_data_len}#|{int(self.ft_root.raw_data_crc)}#${pos}#{self.filename}\r".encode('ASCII')
        self.state = 0
        self.e = False
        self.parm_can_pause = True

    def mode_wait_for_free_tx_buf(self):
        self.start = True
        if self.ft_root.ft_can_start():
            self.state = 1

    def mode_init(self):
        self.send_data(self.header)
        self.state = 2

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
            self.ft_root.ft_rx_buf = b''
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


class BinMODE_TX(DefaultMODE_TX):
    def init(self):
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
            self.ft_root.ft_rx_buf = b''
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


class YappMODE_TX(DefaultMODE_TX):
    def init(self):
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
            ret = self.yapp.yapp_rx(self.ft_root.ft_rx_buf)
            """
            if not ret:
                error_count += 1
            """
            # self.yapp.clean_rx_buf()
            self.ft_root.ft_rx_buf = b''
            # print("Yapp (mode_yapp) rx")
            return
        else:
            # print("Yapp (mode_yapp) Cron")
            self.yapp.yapp_cron()
            return

    def can_send(self):
        """
        if len(self.ft_root.connection.tx_buf_unACK) < self.ft_root.param_MaxFrame:
            return True
        if self.ft_root.ft_can_send():
            return True
        return False
        """
        return True

    def send_data(self, data):
        self.ft_root.ft_tx(data=data)
        # self.ft_root.ft_tx_buf = self.yapp.file_rawdata

    def exec_abort(self):
        self.ft_root.ft_flush_buff()
        self.yapp.exec_abort()
        # self.abort = True
        #self.state = 9
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