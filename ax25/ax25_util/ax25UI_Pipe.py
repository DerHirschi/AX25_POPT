import socket
import threading
import time

import serial

from cfg.default_config import getNew_pipe_cfg
from cfg.logger_config import logger
from fnc.file_fnc import check_file
from fnc.ax25_fnc import validate_ax25Call, build_ax25uid

from ax25.ax25_l2.ax25dec_enc import AX25Frame, via_calls_fm_str
from fnc.socket_fnc import get_ip_by_hostname, check_ip_add_format


class AX25Pipe(object):
    def __init__(self,
                 connection=None,
                 pipe_cfg: dict=None,
                 ):
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
        logger.info("═" * 60)
        logger.info("New AX25Pipe initialized")
        for key, val in pipe_cfg.items():
            logger.info(f"  {key}: {val}")
        logger.info(f"  Connection: {connection}")
        logger.info("═" * 60)
        if not all((
                pipe_cfg.get('pipe_parm_own_call', ''),
                pipe_cfg.get('pipe_parm_address_str', ''),
        )):
            logger.error(f"pipe_parm_own_call : {pipe_cfg.get('pipe_parm_own_call', '')}")
            logger.error(f"pipe_parm_address_str : {pipe_cfg.get('pipe_parm_address_str', '')}")
            raise AttributeError

        if not validate_ax25Call(pipe_cfg.get('pipe_parm_own_call', '')):
            logger.error(f"No valid ax25-Call> {pipe_cfg.get('pipe_parm_own_call', '')}")
            raise AttributeError
        self._add_str   = pipe_cfg.get('pipe_parm_address_str', '')
        self._own_call  = pipe_cfg.get('pipe_parm_own_call', '')
        self._dest_call = self._add_str.split(' ')[0]
        self._via_calls = self._add_str.split(' ')[1:]
        for call in self._via_calls:
            if call:
                if not validate_ax25Call(call):
                    logger.error(f"No valid ax25-Call> {call}")
                    raise AttributeError

        self._pipe_cfg                  = pipe_cfg
        # self._port_id = int(pipe_cfg.get('pipe_parm_port', -1))
        self._parm_pac_len              = pipe_cfg.get('pipe_parm_PacLen', 128)
        self._parm_max_pac              = pipe_cfg.get('pipe_parm_MaxFrame', 3)
        self._parm_max_pac_timer        = pipe_cfg.get('pipe_parm_MaxPacDelay', 30)
        # self._parm_txt_encoder          = pipe_cfg.get('pipe_parm_txt_encoder', 'UTF-8')
        self._parm_txt_encoder          = 'UTF-8'   # For Status Text send frm CLI to User

        if self._connection:
            self._uid = str(self._connection.uid)
        else:
            self._uid = build_ax25uid(
                from_call_str=self._own_call,
                to_call_str=self._dest_call,
                via_calls=self._via_calls,
                dec = False
            )

        """ Ctl """
        self.e_count                                 = 0
        self._max_pac_timer                          = time.time()
        self._work_thread: None | threading.Thread   = None
        self._is_running                             = False
        self._is_error_limit = lambda : self.e_count > 3
        """ I/O buffers. """
        self._tx_data       = bytearray()   # TX to AX25
        self._rx_data       = bytearray()   # RX fm AX25
        self.tx_frame_buf   = []
        """ Backend: 'serial', 'tcp-server', 'tcp-client', 'file' """
        #self._backend_typ        = 'tcp-server' # FIXME: DeleteME
        self._backend_typ        = pipe_cfg.get('pipe_parm_backend', 'file')
        self._backend_loop_timer = time.time()
        self._param_loop_timer   = pipe_cfg.get('pipe_parm_pipe_loop_timer', 10)
        self._device             = None        # Socket/Serial Device
        self._tcp_connection: None | socket.socket  = None  # Client Connection to TCP-Server
        self._tcp_address                           = None  # Client Connection to TCP-Server
        """ Backend init """
        self._init_backend()

    ################################################
    # Backend Init
    def _init_backend(self):
        if self._backend_typ == 'file':
            if not any((
                    self._pipe_cfg.get('pipe_parm_pipe_tx', ''),
                    self._pipe_cfg.get('pipe_parm_pipe_rx', '')
            )):
                logger.error(f"Pipe Tool Backend ({self._backend_typ}) Config Error !!")
                logger.error( "- No TX or RX File configured...")
                raise AttributeError
            self._is_running = True
            if self._pipe_cfg.get('pipe_parm_c_text', ''):
                self._tx_data += self._pipe_cfg.get('pipe_parm_c_text', '').encode(self._parm_txt_encoder, 'ignore')

            logger.info(f"Pipe Tool Backend ({self._backend_typ}) Init done..")
        # Serial
        elif self._backend_typ == 'serial':
            self._be_serial_init()
            logger.info(f"Pipe Tool Backend ({self._backend_typ}) Init done..")
        # TCP-Client
        elif self._backend_typ == 'tcp-client':
            self._be_tcp_client_init()
            logger.info(f"Pipe Tool Backend ({self._backend_typ}) Init done..")
        # TCP-Server
        elif self._backend_typ == 'tcp-server':
            self._be_tcp_server_init()
            logger.info(f"Pipe Tool Backend ({self._backend_typ}) Init done..")
        else:
            logger.error(f"Pipe Tool Backend Typ ({self._backend_typ}) not implemented !!")
            raise AttributeError

    ################################################
    # Crone
    def cron_exec(self):
        """ Called fm Port Handler """
        if not self._is_running:
            return
        if self._backend_loop_timer > time.time():
            return
        if self._backend_typ == 'file':
            self._file_cron()
        elif self._backend_typ == 'serial':
            self._be_serial_cron()
        elif self._backend_typ == 'tcp-client':
            self._be_tcp_client_cron()
        elif self._backend_typ == 'tcp-server':
            self._be_tcp_server_cron()
        else:
            logger.warning(f"Pipe Tool Backend Typ ({self._backend_typ}) not implemented !!")
            return
        self._tx_cron()

    ################################################
    # Backend RX > AX25 TX
    def _tx_cron(self):
        """ TX > AX25 """
        #if not self._is_running:
        #    return
        if not self._tx_data:
            return
        if not self._check_parm_max_pac_timer():
            return
        if self._connection:
            self._tx_Proto()
            return
        self._tx_unProto()

    def _tx_Proto(self):
        if not self._tx_data:
            return
        data = bytearray(self._tx_data)
        self._tx_data = bytearray()
        self._connection.send_data(data)

    def _tx_unProto(self):
        while len(self.tx_frame_buf) < self._parm_max_pac and self._tx_data:
            new_frame = AX25Frame()
            new_frame.from_call.call_str = self._own_call
            new_frame.to_call.call_str   = self._dest_call
            new_frame.via_calls = via_calls_fm_str(' '.join(self._via_calls))
            new_frame.ctl_byte.UIcByte()
            new_frame.pid_byte.pac_types[int(self._pipe_cfg.get('pipe_parm_pid', 0xf0))]()
            new_frame.ctl_byte.cmd  = self._pipe_cfg.get('pipe_parm_cmd_pf', (False, False))[0]
            new_frame.ctl_byte.pf   = self._pipe_cfg.get('pipe_parm_cmd_pf', (False, False))[1]
            new_frame.payload       = self._tx_data[:min(len(self._tx_data), self._parm_pac_len)]
            self._tx_data           = self._tx_data[min(len(self._tx_data), self._parm_pac_len):]
            new_frame.encode_ax25frame()
            self.tx_frame_buf.append(new_frame)

    ################################################
    # TX - Helper
    def _set_parm_max_pac_timer(self):
        self._max_pac_timer = self._parm_max_pac_timer + time.time()

    def _check_parm_max_pac_timer(self):
        if self._max_pac_timer > time.time():
            return False
        self._set_parm_max_pac_timer()
        return True

    ################################################
    # AX25 RX > Backend TX
    def handle_rx(self, ax25_frame):
        """ ax25Port """
        return self.handle_rx_rawdata(ax25_frame.payload)

    def handle_rx_rawdata(self, raw_data: b''):
        """ ax25Connection """
        if not self._is_running or self._is_error_limit():
            return False
        self._rx_data += raw_data
        if self._backend_typ == 'file':
            return self._save_rx_buff_to_file()
        elif self._backend_typ == 'serial':
            return self._be_serial_tx()
        elif self._backend_typ == 'tcp-client':
            return self._be_tcp_client_tx()
        elif self._backend_typ == 'tcp-server':
            return self._be_tcp_server_tx()
        else:
            logger.warning(f"Pipe Tool Backend Typ ({self._backend_typ}) not implemented !!")
            return False


    # ====================================================================
    # Pipe <> File
    def _file_cron(self):
        if not self._pipe_cfg.get('pipe_parm_pipe_tx', ''):
            return
        if self._is_error_limit():
            self.close_pipe(disco_ax25=True)
            self._backend_loop_timer = time.time() + 5
            return
        if hasattr(self._work_thread, 'is_alive'):
            if self._work_thread.is_alive():
                return
        if hasattr(self._work_thread, 'join'):
            self._work_thread.join()

        self._backend_loop_timer = time.time() + self._param_loop_timer
        """"""
        self._work_thread = threading.Thread(target=self._load_tx_buff_fm_file)
        self._work_thread.start()

    def _load_tx_buff_fm_file(self):
        if not self._pipe_cfg.get('pipe_parm_pipe_tx', ''):
            return False
        if not check_file:
            self.e_count += 1
            return False
        try:
            with open(self._pipe_cfg.get('pipe_parm_pipe_tx', ''), 'rb') as f:
                self._tx_data += f.read()
        except (PermissionError, FileNotFoundError):
            self.e_count += 1
            return False
        try:
            with open(self._pipe_cfg.get('pipe_parm_pipe_tx', ''), 'wb') as f:
                f.write(b'')
        except (PermissionError, FileNotFoundError):
            self.e_count += 1
            return False
        self.e_count = 0
        return True

    def _save_rx_buff_to_file(self):
        if not self._pipe_cfg.get('pipe_parm_pipe_rx', ''):
            return False
        if not self._rx_data:
            return True
        if not check_file(self._pipe_cfg.get('pipe_parm_pipe_rx', '')):
            self.e_count += 1
            return False
        try:
            with open(self._pipe_cfg.get('pipe_parm_pipe_rx', ''), 'ab') as f:
                f.write(self._rx_data)
                self._rx_data = bytearray()
        except (PermissionError, FileNotFoundError):
            self.e_count += 1
            return False
        self.e_count = 0
        return True

    # ====================================================================
    # Pipe <> TCP Server
    def _be_tcp_server_init(self):
        server_ip, server_port = self._pipe_cfg.get('pipe_be_address', ('0.0.0.0', 8023))
        # server_ip, server_port = ('0.0.0.0', 25522)

        if not all((check_ip_add_format(server_ip), server_port)):
            logger.error(f"Pipe ({self._backend_typ}) no Server Address or Port configured!")
            logger.error(f"  IP     : {server_ip}")
            logger.error(f"  Port   : {server_port}")
            raise AttributeError
        try:
            self._device = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._device.settimeout(0.5)
            self._device.bind((server_ip, server_port))
            self._device.listen(1)
        except Exception as ex:
            logger.error(f"Pipe ({self._backend_typ}): can't init Device !!")
            logger.error(f"  {ex}")
            raise ex

        self._is_running = True

    def _be_tcp_server_cron(self):
        if self._is_error_limit():
            self.close_pipe(disco_ax25=True)
            self._backend_loop_timer = time.time() + 5
            return

        if hasattr(self._work_thread, 'is_alive'):
            if self._work_thread.is_alive():
                return
        if hasattr(self._work_thread, 'join'):
            self._work_thread.join()
        self._backend_loop_timer = time.time() + 0.5

        if self._tcp_connection is None:
            target = self._be_tcp_server_wait_f_client
        else:
            target = self._be_tcp_server_rx

        self._work_thread = threading.Thread(target=target)
        self._work_thread.start()

    def _be_tcp_server_wait_f_client(self):
        try:
            self._tcp_connection, self._tcp_address = self._device.accept()
            self.e_count = 0
            logger.info(f"Pipe ({self._backend_typ}): {self._tcp_address} has connected to the Pipe-Server ...")
        except OSError:
            # Timeout
            return
        except Exception as ex:
            logger.error(f"Pipe ({self._backend_typ}): Connection Error !!")
            logger.error(ex)
            self.e_count += 1
            self._tx_data += ' # Pipe Error: Connection Error\r'.encode(self._parm_txt_encoder, 'ignore')
            self.close_pipe(disco_ax25=True)
            return
        send_at_init     = self._pipe_cfg.get('pipe_be_send_at_init', '')
        c_text           = self._pipe_cfg.get('pipe_parm_c_text', '')
        if send_at_init:
            self._rx_data += send_at_init.encode(self._parm_txt_encoder, 'ignore')
            self._be_tcp_server_tx()

        if c_text:
            self._tx_data += c_text.encode(self._parm_txt_encoder, 'ignore')

    def _be_tcp_server_rx(self):
        """ TCP-Server RX > AX25 TX """
        if not self._is_running or self._is_error_limit():
            return
        try:
            data = self._tcp_connection.recv(4096)
            if not data:
                logger.info(f"Pipe ({self._backend_typ}): Connection closed by Client !!")
                self.close_pipe(disco_ax25=True)
                return

            self._tx_data += data
            return
        except socket.timeout:
            return
        except Exception as ex:
            logger.error(f"Pipe ({self._backend_typ}): Server Error while receiving from Client !!")
            logger.error(f"  Address: {self._tcp_address}")
            logger.error(f"  {ex}")
            self._is_running = False
            self.e_count = 10
            self._tx_data += ' # Pipe Error: Server Error !!\r'.encode(self._parm_txt_encoder, 'ignore')
            self.close_pipe(disco_ax25=True)
            return

    def _be_tcp_server_tx(self):
        """ AX25 RX > TCP-Server TX """
        if not self._is_running or self._is_error_limit():
            return False
        data = self._rx_data
        self._rx_data = bytearray()
        try:
            self._tcp_connection.sendall(data)
            return True

        except Exception as ex:
            logger.error(f"Pipe ({self._backend_typ}): Server Error while sending to Client !!")
            logger.error(f"  Address: {self._tcp_address}")
            logger.error(f"  {ex}")
            self._is_running = False
            self.e_count = 10
            self._tx_data += ' # Pipe Error: Server Error\r'.encode(self._parm_txt_encoder, 'ignore')
            self.close_pipe(disco_ax25=True)
            return False

    # ====================================================================
    # Pipe <> TCP Client
    def _be_tcp_client_init(self):
        client_address, client_port = self._pipe_cfg.get('pipe_be_address',           ('', 0))
        send_at_init                = self._pipe_cfg.get('pipe_be_send_at_init',      '')
        flush_rx_at_init            = self._pipe_cfg.get('pipe_be_flush_rx_at_init',  False)
        c_text                      = self._pipe_cfg.get('pipe_parm_c_text',          '')
        # Resolve Domain name
        client_ip = get_ip_by_hostname(client_address)

        if not all((check_ip_add_format(client_ip), client_port)):
            logger.error(f"Pipe ({self._backend_typ}) no Server Address or Port configured!")
            logger.error(f"  Address: {client_address}")
            logger.error(f"  IP     : {client_ip}")
            logger.error(f"  Port   : {client_port}")
            raise AttributeError
        try:
            self._device = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as ex:
            logger.error(f"Pipe ({self._backend_typ}): can't init Device !!")
            logger.error(f"  {ex}")
            raise ex
        try:
            self._device.connect((client_ip, client_port))
            # <<< HIER KEEPALIVE AKTIVIEREN >>>
            #self._device.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

            # Optional: Keepalive-Parameter feiner einstellen (Linux/macOS/Windows)
            #if hasattr(socket, 'TCP_KEEPIDLE'):
            #    self._device.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10)  # nach 10s Inaktivität starten
            #if hasattr(socket, 'TCP_KEEPCNT'):
            #    self._device.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)  # max. 3 Probes
            #if hasattr(socket, 'TCP_KEEPINTVL'):
            #    self._device.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)  # alle 5s eine Probe
            self._device.settimeout(0.4)
        except Exception as ex:
            logger.error(f"Pipe ({self._backend_typ}): can't Connect to Server !!")
            logger.error(f"  Address: {client_address}")
            logger.error(f"  IP     : {client_ip}")
            logger.error(f"  Port   : {client_port}")
            logger.error(f"  {ex}")
            self.e_count = 10
            self.close_pipe()
            raise ex

        if flush_rx_at_init:
            try:
                rx_data = self._device.recv(4096)
                logger.info(f"Pipe ({self._backend_typ}): {client_address}")
                logger.info( "  Flushing Connection Init Data:")
                logger.info("")
                logger.info(f"{rx_data}")
            except socket.timeout:
                pass

        self._device.settimeout(0.4)
        self._is_running = True

        if send_at_init:
            self._rx_data += send_at_init.encode(self._parm_txt_encoder, 'ignore')
            self._be_tcp_client_tx()

        if c_text:
            self._tx_data += c_text.encode(self._parm_txt_encoder, 'ignore')

    """
    def _be_tcp_client_reinit(self):
        if self._is_error_limit():
            if self._is_running or self._connection:
                self.close_pipe(disco_ax25=True)
            return False
        logger.info(f"Pipe ({self._backend_typ}): Reinit Connection to TCP-Sever !!")
        logger.info(f"  Address: {self._pipe_cfg.get('pipe_be_address', ('', 0))}")
        self.close_pipe(wait=True)
        try:
            self._be_tcp_client_init()
            self.e_count = 0
            return True
        except Exception as ex:
            logger.error(f"Pipe ({self._backend_typ}): can't Connect to Server !!")
            logger.error(f"  Address: {self._pipe_cfg.get('pipe_be_address', ('', 0))}")
            logger.error(f"  {ex}")
            self._tx_data += ' # Pipe Error: Connection Error\r'.encode(self._parm_txt_encoder, 'ignore')
            self.e_count = 10
            self.close_pipe(disco_ax25=True)
            return False
    """

    def _be_tcp_client_cron(self):
        if self._is_error_limit():
            self.close_pipe(disco_ax25=True)
            self._backend_loop_timer = time.time() + 5
            return

        if hasattr(self._work_thread, 'is_alive'):
            if self._work_thread.is_alive():
                return
        if hasattr(self._work_thread, 'join'):
            self._work_thread.join()
        self._backend_loop_timer = time.time() + 0.5

        self._work_thread = threading.Thread(target=self._be_tcp_client_rx)
        self._work_thread.start()

    def _be_tcp_client_tx(self):
        """ AX25 RX > TCP-Client TX """
        if not self._is_running or self._is_error_limit():
            return False
        data = self._rx_data
        self._rx_data = bytearray()
        try:
            self._device.sendall(data)
            return True

        except Exception as ex:
            logger.error(f"Pipe ({self._backend_typ}): can't Connect to Server !!")
            logger.error(f"  Address: {self._pipe_cfg.get('pipe_be_address', ('', 0))}")
            logger.error(f"  {ex}")
            self.e_count = 10
            self._tx_data += ' # Pipe Error: Connection Error\r'.encode(self._parm_txt_encoder, 'ignore')
            self.close_pipe(disco_ax25=True)
            return False

    def _be_tcp_client_rx(self):
        """ TCP-Client RX > AX25 TX """
        if not self._is_running or self._is_error_limit():
            return
        try:
            data = self._device.recv(4096)
            if not data:
                logger.info(f"Pipe ({self._backend_typ}): Connection closed by Server !!")
                self.e_count = 10
                self.close_pipe(disco_ax25=True)
                return
            self._tx_data += data
            return
        except socket.timeout:
            return
        except Exception as ex:
            logger.error(f"Pipe ({self._backend_typ}): can't Connect to Server !!")
            logger.error(f"  Address: {self._pipe_cfg.get('pipe_be_address', ('', 0))}")
            logger.error(f"  {ex}")
            self._is_running = False
            self.e_count = 10
            self._tx_data += ' # Pipe Error: Connection Error to Server\r'.encode(self._parm_txt_encoder, 'ignore')
            self.close_pipe(disco_ax25=True)
            return

    # ====================================================================
    # Pipe <> Serial
    def _be_serial_init(self):
        ser_port, ser_baud = self._pipe_cfg.get('pipe_be_address', ('', 0))
        send_at_init       = self._pipe_cfg.get('pipe_be_send_at_init', '')
        flush_rx_at_init   = self._pipe_cfg.get('pipe_be_flush_rx_at_init', False)

        if not all((ser_port, ser_baud)):
            logger.error(f"Pipe ({self._backend_typ}) no Serial-Port or Serial-Baud configured!")
            logger.error(f"  Port   : {ser_port}")
            logger.error(f"  Baud   : {ser_baud}")
            raise AttributeError
        try:
            self._device = serial.Serial(
                ser_port,
                ser_baud,
                timeout=0.4
            )
        except Exception as ex:
            logger.error(f"Pipe ({self._backend_typ}) Init-Error!")
            logger.error(f"  Port   : {ser_port}")
            logger.error(f"  Baud   : {ser_baud}")
            logger.error(ex)
            raise ex

        if flush_rx_at_init:
            self._device.flush()

        self._is_running = True
        if send_at_init:
            self._rx_data += send_at_init.encode(self._parm_txt_encoder, 'ignore')
            self._be_serial_tx()

    """
    def _be_serial_reinit(self):
        if self._is_error_limit():
            if self._is_running or self._connection:
                self.close_pipe(disco_ax25=True)
            return False
        logger.info(f"Pipe ({self._backend_typ}): Reinit Connection to Serial-Device !!")
        logger.info(f"  Address: {self._pipe_cfg.get('pipe_be_address', ('', 0))}")
        self.close_pipe(wait=True)
        try:
            self._be_serial_init()
            self.e_count = 0
            return True
        except Exception as ex:
            logger.error(f"Pipe ({self._backend_typ}): can't Connect to Serial-Device !!")
            logger.error(f"  Address: {self._pipe_cfg.get('pipe_be_address', ('', 0))}")
            logger.error(f"  {ex}")
            self._tx_data += ' # Pipe Error: Connection Error\r'.encode(self._parm_txt_encoder, 'ignore')
            self.e_count = 10
            self.close_pipe(disco_ax25=True)
            return False
    """

    def _be_serial_cron(self):
        if self._is_error_limit():
            self.close_pipe(disco_ax25=True)
            self._backend_loop_timer = time.time() + 5
            return

        if hasattr(self._work_thread, 'is_alive'):
            if self._work_thread.is_alive():
                return
        if hasattr(self._work_thread, 'join'):
            self._work_thread.join()
        self._backend_loop_timer = time.time() + 0.5

        self._work_thread = threading.Thread(target=self._be_serial_rx)
        self._work_thread.start()

    def _be_serial_tx(self):
        """ AX25 RX > Serial TX """
        run_timer = time.time()
        if not self._is_running or self._is_error_limit():
            return False
        data = self._rx_data
        self._rx_data = bytearray()
        try:
            self._device.write(data)
            logger.debug(f"Pipe ({self._backend_typ}) Runtime TX: {round((time.time() - run_timer), 2)} Sec.")
            return True

        except Exception as ex:
            logger.error(f"Pipe ({self._backend_typ}): can't Connect to Serial Device !!")
            logger.error(f"  Address: {self._pipe_cfg.get('pipe_be_address', ('', 0))}")
            logger.error(f"  {ex}")
            self.e_count = 10
            self._tx_data += ' # Pipe Error: Connection Error\r'.encode(self._parm_txt_encoder, 'ignore')
            self.close_pipe(disco_ax25=True)
            return False

    def _be_serial_rx(self):
        """ Serial Device RX > AX25 TX """
        if not self._is_running or self._is_error_limit():
            return
        while self._is_running and not self._is_error_limit():
            try:
                data = self._device.read()
                if not data:
                    return
                self._tx_data += data
            except Exception as ex:
                logger.error(f"Pipe ({self._backend_typ}): can't read from Serial Device !!")
                logger.error(f"  Address: {self._pipe_cfg.get('pipe_be_address', ('', 0))}")
                logger.error(f"  {ex}")
                self._is_running = False
                self.e_count = 10
                self._tx_data += ' # Pipe Error: Connection Error to Server\r'.encode(self._parm_txt_encoder, 'ignore')
                self.close_pipe(disco_ax25=True)
                return

    ################################################
    # End
    def close_pipe(self, wait=False, disco_ax25=False):
        logger.info("Closing Pipe")
        if self._connection:
            self._tx_Proto()
        try:
            self._device.settimeout(0.1)
        except AttributeError:
            pass
        except Exception as ex:
            logger.warning("Error while closing Pipe")
            logger.warning(ex)
        self._is_running = False
        try:
            self._tcp_connection.shutdown(socket.SHUT_RDWR)
            self._device.shutdown(socket.SHUT_RDWR)
            self._device.close()
        except (OSError, AttributeError):
            pass
        except Exception as ex:
            logger.warning("Pipe Tool Shutdown....")
            logger.warning(ex)
        if disco_ax25:
            if hasattr(self._connection, 'conn_disco'):
                self._connection.conn_disco()
        if not wait:
            return
        if not hasattr(self._work_thread, 'is_alive'):
            return
        while self._work_thread.is_alive():
            logger.info("Waiting for Pipe Thread to be closed")
            self._work_thread.join(timeout=0.3)

    ################################################
    # Geta
    def get_cfg_fm_pipe(self):
        return self._pipe_cfg

    def get_pipe_connection(self):
        return self._connection

    def get_pipe_uid(self):
        return self._uid

    def get_tx_data(self, del_buffer=True):
        if del_buffer:
            data = bytes(self._tx_data)
            self._tx_data = bytearray()
            return data
        return bytes(self._tx_data)

    def get_thread(self):
        return self._work_thread

    def is_error(self):
        return self._is_error_limit()