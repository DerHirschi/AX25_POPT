import time

from cfg.default_config import getNew_pipe_cfg
from cfg.logger_config import logger
from fnc.file_fnc import check_file
from fnc.ax25_fnc import validate_ax25Call, build_ax25uid

from ax25.ax25dec_enc import AX25Frame, via_calls_fm_str


class AX25Pipe(object):
    def __init__(self,
                 connection=None,
                 pipe_cfg: dict=None,
                 ):
        self.e_count = 0
        if not connection and not pipe_cfg:
            raise AttributeError

        self._connection = connection
        if not pipe_cfg and connection:
            pipe_cfg = getNew_pipe_cfg()
        if connection:
            pipe_cfg['pipe_parm_own_call']      = str(connection.my_call_str)
            pipe_cfg['pipe_parm_address_str']   = f'{connection.to_call_str} ' + ' '.join(connection.via_calls)
            pipe_cfg['pipe_parm_port']          = int(connection.own_port.port_id)
            pipe_cfg['pipe_parm_Proto']         = True
            pipe_cfg['pipe_parm_permanent']     = False
            pipe_cfg['pipe_parm_PacLen']        = 0
            pipe_cfg['pipe_parm_MaxFrame']      = 0
            # pipe_cfg['pipe_parm_pipe_tx'] = f'{connection.ch_index}-{connection.my_call_str}-{connection.to_call_str}-tx.txt'
            # pipe_cfg['pipe_parm_pipe_rx'] = f'{connection.ch_index}-{connection.my_call_str}-{connection.to_call_str}-rx.txt'

        if not all((
                pipe_cfg.get('pipe_parm_own_call', ''),
                pipe_cfg.get('pipe_parm_address_str', ''),
                # pipe_cfg.get('pipe_parm_pipe_tx', ''),
                # pipe_cfg.get('pipe_parm_pipe_rx', ''),
        )):
            logger.error(f"pipe_parm_own_call : {pipe_cfg.get('pipe_parm_own_call', '')}")
            logger.error(f"pipe_parm_address_str : {pipe_cfg.get('pipe_parm_address_str', '')}")
            logger.error(f"pipe_parm_own_call : {pipe_cfg.get('pipe_parm_pipe_tx', '')}")
            logger.error(f"pipe_parm_own_call : {pipe_cfg.get('pipe_parm_pipe_rx', '')}")
            raise AttributeError

        if not validate_ax25Call(pipe_cfg.get('pipe_parm_own_call', '')):
            logger.error(f"No valid ax25-Call> {pipe_cfg.get('pipe_parm_own_call', '')}")
            raise AttributeError

        logger.debug("New Pipe !")
        for p_name, param in pipe_cfg.items():
            logger.debug(f"{p_name}: {param}")
        logger.debug(f"Conn: {connection}")

        self._pipe_cfg = pipe_cfg
        self._tx_filename = pipe_cfg.get('pipe_parm_pipe_tx', '')
        self._rx_filename = pipe_cfg.get('pipe_parm_pipe_rx', '')
        self._parm_tx_file_check_timer = pipe_cfg.get('pipe_parm_pipe_loop_timer', 10)
        # self._port_id = int(pipe_cfg.get('pipe_parm_port', -1))
        self._parm_pac_len = pipe_cfg.get('pipe_parm_PacLen', 128)
        self._parm_max_pac = pipe_cfg.get('pipe_parm_MaxFrame', 3)
        self._parm_max_pac_timer = pipe_cfg.get('pipe_parm_MaxPacDelay', 30)
        # self._isProto = pipe_cfg.get('pipe_parm_Proto', True)
        self._add_str = pipe_cfg.get('pipe_parm_address_str', '')
        self._own_call = pipe_cfg.get('pipe_parm_own_call', '')
        self._dest_call = self._add_str.split(' ')[0]
        self._via_calls = self._add_str.split(' ')[1:]
        for call in self._via_calls:
            if call:
                if not validate_ax25Call(call):
                    logger.error(f"No valid ax25-Call> {call}")

                    raise AttributeError

        if self._connection:
            self._uid = self._connection.uid
        else:
            self._uid = build_ax25uid(
                from_call_str=self._own_call,
                to_call_str=self._dest_call,
                via_calls=self._via_calls,
                dec = False
            )
        self._max_pac_timer = time.time()
        self._tx_file_check_timer = time.time()
        """ Buffers buffers buffers. """
        self._tx_data = bytearray()
        self._rx_data = bytearray()
        self.tx_frame_buf = []
        """ Proto Pipe """

    def cron_exec(self):
        if self._tx_filename or self._rx_filename:
            self._tx_file_cron()
            self._tx_cron()

    def _tx_file_cron(self):
        if self._tx_file_check_timer < time.time():
            self._tx_file_check_timer = time.time() + self._parm_tx_file_check_timer
            """"""
            self._load_tx_buff_fm_file()

    def _tx_cron(self):
        if self._tx_data:
            if self._check_parm_max_pac_timer():
                self._tx_unProto()
                self._tx_Proto()

    def _tx_unProto(self):
        if self._connection is None:
            while len(self.tx_frame_buf) < self._parm_max_pac and self._tx_data:
                new_frame = AX25Frame()
                new_frame.from_call.call_str = self._own_call
                new_frame.to_call.call_str = self._dest_call
                new_frame.via_calls = via_calls_fm_str(' '.join(self._via_calls))
                new_frame.ctl_byte.UIcByte()
                new_frame.pid_byte.pac_types[int(self._pipe_cfg.get('pipe_parm_pid', 0xf0))]()
                new_frame.ctl_byte.cmd = self._pipe_cfg.get('pipe_parm_cmd_pf', (False, False))[0]
                new_frame.ctl_byte.pf = self._pipe_cfg.get('pipe_parm_cmd_pf', (False, False))[1]
                new_frame.payload = self._tx_data[:min(len(self._tx_data), self._parm_pac_len)]
                self._tx_data = self._tx_data[min(len(self._tx_data), self._parm_pac_len):]
                new_frame.encode_ax25frame()
                self.tx_frame_buf.append(new_frame)

    def _tx_Proto(self):
        if self._connection:
            self._connection.send_data(bytearray(self._tx_data))
            self._tx_data = bytearray()

    def _set_parm_max_pac_timer(self):
        self._max_pac_timer = self._parm_max_pac_timer + time.time()

    def _check_parm_max_pac_timer(self):
        if self._max_pac_timer < time.time():
            self._set_parm_max_pac_timer()
            return True
        return False

    def handle_rx(self, ax25_frame):
        self._rx_data += ax25_frame.payload
        return self._save_rx_buff_to_file()

    def handle_rx_rawdata(self, raw_data: b''):
        self._rx_data += raw_data
        return self._save_rx_buff_to_file()

    def _load_tx_buff_fm_file(self):
        if self._tx_filename:
            if check_file:
                try:
                    with open(self._tx_filename, 'rb') as f:
                        self._tx_data += f.read()
                except (PermissionError, FileNotFoundError):
                    self.e_count += 1
                    return False
                else:
                    try:
                        with open(self._tx_filename, 'wb') as f:
                            f.write(b'')
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
        if self._rx_filename:
            if self._rx_data:
                if check_file(self._rx_filename):
                    try:
                        with open(self._rx_filename, 'ab') as f:
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

    def get_cfg_fm_pipe(self):
        return self._pipe_cfg

    def get_pipe_connection(self):
        return self._connection

    def get_pipe_uid(self):
        return self._uid
