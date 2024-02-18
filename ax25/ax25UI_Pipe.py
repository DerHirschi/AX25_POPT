import time
from fnc.file_fnc import check_file
from fnc.ax25_fnc import reverse_uid

from ax25.ax25dec_enc import AX25Frame, via_calls_fm_str


class AX25Pipe(object):
    tx_filename = ''
    rx_filename = ''
    parm_tx_file_check_timer = 10

    def __init__(self,
                 port_id: int = -1,
                 own_call: str = 'NOCALL',
                 address_str: str = 'NOCALL',
                 cmd_pf: tuple = (False, False),
                 pid: hex = 0xf0
                 ):
        """ This Init Sucks """
        dest_add = via_calls_fm_str(address_str)
        self.add_str = address_str
        self.ax25_frame = AX25Frame()
        self.ax25_frame.from_call.call_str = own_call
        if dest_add:
            self.ax25_frame.to_call.call_str = dest_add[0].call_str
            if len(dest_add) > 1:
                self.ax25_frame.via_calls = dest_add[1:]
        self.ax25_frame.ctl_byte.UIcByte()
        self.ax25_frame.ctl_byte.cmd = cmd_pf[0]
        self.ax25_frame.ctl_byte.pf = cmd_pf[1]
        self.ax25_frame.pid_byte.pac_types[int(pid)]()
        self.uid = self.ax25_frame.addr_uid
        self.port_id = int(port_id)
        self.parm_pac_len = 128
        self.parm_max_pac = 3
        self.parm_max_pac_timer = 30
        self._max_pac_timer = time.time()
        self._tx_file_check_timer = time.time()
        self.e_count = 0
        """ Buffers buffers buffers. We have Ram, so we need more buffer. """
        self._tx_data = b''
        self._rx_data = b''
        self.tx_frame_buf: [AX25Frame] = []
        """ Protocoled Pipe """
        self.connection = None

    def cron_exec(self):
        # self.save_rx_buff_to_file()
        if self.tx_filename or self.rx_filename:
            self._tx_file_cron()
            self._tx_cron()

    def _tx_file_cron(self):
        if self._tx_file_check_timer < time.time():
            self._tx_file_check_timer = time.time() + self.parm_tx_file_check_timer
            """"""
            self._load_tx_buff_fm_file()

    def _tx_cron(self):
        if self._tx_data:
            if self._check_parm_max_pac_timer():
                self._tx_unProto()
                self._tx_Proto()

    def _tx_unProto(self):
        if self.connection is None:
            while len(self.tx_frame_buf) < self.parm_max_pac and self._tx_data:
                new_frame = AX25Frame()
                new_frame.from_call = self.ax25_frame.from_call
                new_frame.to_call = self.ax25_frame.to_call
                new_frame.via_calls = self.ax25_frame.via_calls
                new_frame.pid_byte = self.ax25_frame.pid_byte
                new_frame.ctl_byte = self.ax25_frame.ctl_byte
                new_frame.data = self._tx_data[:min(len(self._tx_data), self.parm_pac_len)]
                self._tx_data = self._tx_data[min(len(self._tx_data), self.parm_pac_len):]
                new_frame.encode_ax25frame()
                self.tx_frame_buf.append(new_frame)

    def _tx_Proto(self):
        if self.connection:
            self.connection.tx_buf_rawData += bytes(self._tx_data)
            self._tx_data = b''

    def _set_parm_max_pac_timer(self):
        self._max_pac_timer = self.parm_max_pac_timer + time.time()

    def set_dest_add(self, address_str):
        dest_add = via_calls_fm_str(address_str)
        self.ax25_frame.to_call.call_str = dest_add[0].call_str
        if len(dest_add) > 1:
            self.ax25_frame.via_calls = dest_add[1:]

    def change_settings(self):
        if self.connection:
            self.ax25_frame = self.connection.ax25_out_frame
        if not self.ax25_frame.from_call.call_str:
            return False
        if not self.ax25_frame.to_call.call_str:
            return False
        self.ax25_frame.encode_ax25frame()
        self.uid = self.ax25_frame.addr_uid
        self.add_str = ' '.join(reverse_uid(self.uid).split(':')[1:])

        self._rx_data += self.ax25_frame.to_call.call_str.encode() + b' ' + self.uid.encode() + b'\r'  # Maybe optional
        self._save_rx_buff_to_file()
        return True

    def _check_parm_max_pac_timer(self):
        if self._max_pac_timer < time.time():
            self._set_parm_max_pac_timer()
            return True
        return False

    def handle_rx(self, ax25_frame: AX25Frame):
        self._rx_data += ax25_frame.data
        return self._save_rx_buff_to_file()

    def handle_rx_rawdata(self, raw_data: b''):
        self._rx_data += raw_data
        return self._save_rx_buff_to_file()

    def _load_tx_buff_fm_file(self):
        if self.tx_filename:
            if check_file:
                try:
                    with open(self.tx_filename, 'rb') as f:
                        self._tx_data += f.read()
                except (PermissionError, FileNotFoundError):
                    self.e_count += 1
                    return False
                else:
                    try:
                        with open(self.tx_filename, 'wb') as f:
                            pass
                    except (PermissionError, FileNotFoundError):
                        self.e_count += 1
                        return False
                self.e_count = 0
                return True
            else:
                self.e_count += 1
                return False
        return True

    def _save_rx_buff_to_file(self):
        if self.rx_filename:
            if self._rx_data:
                if check_file(self.rx_filename):
                    try:
                        with open(self.rx_filename, 'ab') as f:
                            f.write(self._rx_data)
                            self._rx_data = b''
                            self.e_count = 0
                            return True
                    except (PermissionError, FileNotFoundError):
                        self.e_count += 1
                        return False
                self.e_count += 1
                return False
        return True

