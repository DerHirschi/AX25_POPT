import socket
import time

from ax25.ax25Error import AX25DeviceFAIL, AX25DeviceERROR
from ax25.ax25_l2.ax25Kiss import Kiss
from .ax25Port import AX25Port
from .ax25Port_Classes import RxBuf
from cfg.logger_config import logger


class TNC_EMU_TCP_SRV(AX25Port):
    def __init__(self, port_id: int, port_handler):
        super().__init__(port_id, port_handler)
        self.tnc_protocol = Kiss(self._port_cfg)
        if self.is_multi_ch_slave():
            if self.multi_ch_tnc.init_multi_channel_tnc():
                return
            AX25DeviceFAIL(self)
        try:
            self.init()
        except AX25DeviceFAIL:
            # raise AX25DeviceFAIL(self)  # TODO in PortINIT
            AX25DeviceFAIL(self)

    def init(self):
        if self._loop_is_running:
            logger.info(f'Port {self.port_id}: TNC-EMU-TCP-SRV INIT')
            sock_timeout = 1
            self.tnc_protocol.is_enabled = True
            self.tnc_protocol.set_param = False

            try:
                self.device = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except PermissionError as e:
                logger.error(f'Port {self.port_id}:Error. Cant connect to KISS TCP Device {self._port_param}')
                logger.error('{}'.format(e))
                self._loop_is_running = False
                self.device = None
                raise AX25DeviceFAIL
            try:
                self.device.settimeout(sock_timeout)
                self.device.bind(self._port_param)
                self.device.listen(1)
                self.device_is_running = True

            except (OSError, ConnectionRefusedError, ConnectionError) as e:
                logger.error(f'Port {self.port_id}: Error. Cant open TNC-EMU Device {self._port_param}')
                logger.error('{}'.format(e))
                # self.device.shutdown(socket.SHUT_RDWR)
                # self.device.close()
                self.close_device()
                raise AX25DeviceFAIL


    def __del__(self):
        # self.device.shutdown(socket.SHUT_RDWR)
        self.close_device()

    def close_device(self):
        self._loop_is_running = False
        if self.device is None:
            self.device_is_running = False
            return
        try:
            # Deactivate KISS Mode on TNC
            """
            if self.kiss.is_enabled:
                self.device.sendall(self.kiss.device_kiss_end())
            """
            # self.device.shutdown(socket.SHUT_RDWR)
            if self._tnc_emu_connection is not None:
                self._tnc_emu_connection.close()
            self.device.close()
        except (OSError, ConnectionRefusedError, ConnectionError, AttributeError) as e:
            logger.error(f"Port {self.port_id}: Error while closing Port !")
            logger.error(f"Port {self.port_id}: {e}")
            self.device_is_running = False
            if self.device is not None:
                try:
                    self.device.close()
                except (OSError, ConnectionRefusedError, ConnectionError, AttributeError) as e:
                    logger.error(f"Port {self.port_id}: Error while closing Port !")
                    logger.error(f"Port {self.port_id}: {e}")
                    return
        finally:
            self.device_is_running = False
            if self.device is not None:
                self.device.close()
            # print("KISS TCP FINALLY")

    def set_kiss_parm(self):
        if self.tnc_protocol.protocol_name != 'KISS':
            return
        if self.tnc_protocol.is_enabled and self.device is not None and self.device_is_running and self.tnc_protocol.set_param:
            try:
                self.device.sendall(self.tnc_protocol.set_all_parameter())
            except (OSError, ConnectionRefusedError, ConnectionError, socket.timeout) as e:
                logger.error(f"Port {self.port_id}: SetKiss Failed !! {e}")
                logger.error('{}'.format(e))
                raise AX25DeviceFAIL

    def _rx(self):
        #self.port_w_dog = time.time()
        recv_buff = b''
        if self._tnc_emu_connection is None:
            try:
                self._tnc_emu_connection, self._tnc_emu_client_address = self.device.accept()
            except OSError:
                # Timeout
                return None
            logger.info(
                f'Port {self.port_id}: TNC-EMU Device: Client connection accepted. {self._tnc_emu_client_address}')
            self._tnc_emu_connection.settimeout(0.2)
            kiss_start_cmd = self.tnc_protocol.device_start()
            if all((self.tnc_protocol.is_enabled, kiss_start_cmd, self.tnc_protocol.set_param)):

                # self.device.sendall(self.kiss.device_kiss_start_1())
                try:
                    self.device.sendall(self.tnc_protocol.device_start())
                    # print(self.device.recv(999))
                except BrokenPipeError as e:
                    # print('{}'.format(e))
                    logger.error(f'Port {self.port_id}: {e}')
                    # self.device.shutdown(socket.SHUT_RDWR)
                    # self.device.close()
                    self.close_device()
                    raise AX25DeviceFAIL
                else:
                    try:
                        self.set_kiss_parm()
                    except AX25DeviceFAIL as e:
                        raise e
            return None
        else:
            while self._loop_is_running and self.device_is_running:
                try:
                    recv_buff += self._tnc_emu_connection.recv(1)
                except socket.timeout:
                    # if not recv_buff:
                    return None
                except OSError as e:
                    self._tnc_emu_connection, self._tnc_emu_client_address = None, None
                    raise AX25DeviceERROR(e, self)

                if recv_buff:
                    de_kiss_fr = self.tnc_protocol.decode_tnc_multi_ch(recv_buff)
                    if de_kiss_fr is not None:
                        ret = RxBuf()
                        ret.raw_data = bytes(de_kiss_fr)
                        ret.kiss_frame = bytes(recv_buff)
                        return ret
                    if self.tnc_protocol.unknown_kiss_frame(recv_buff):
                        recv_buff = b''

                else:
                    if self._tnc_emu_connection is not None:
                        logger.info(f'Port {self.port_id}: TNC-EMU Device: Closing Client connection')
                        self._tnc_emu_connection.close()
                        self._tnc_emu_connection, self._tnc_emu_client_address = None, None
                    return None
            return None

    def _tx_device(self, frame, tnc_channel=0):
        if self._tnc_emu_connection is None:
            return
        ###################################
        try:
            self._tnc_emu_connection.sendall(self.tnc_protocol.encode_tnc(frame.data_bytes, tnc_channel))
        except (ConnectionRefusedError, ConnectionError, BrokenPipeError) as e:
            logger.warning(
                f'Port {self.port_id}: Error. TNC-EMU Device. Try Reinit Device {self._port_param}')
            logger.warning('{}'.format(e))
            self._tnc_emu_connection, self._tnc_emu_client_address = None, None

        except (OSError, socket.timeout) as e:
            logger.error(
                f'Port {self.port_id}: Error. Cant send Packet to TNC-EMU Device. Try Reinit Device {self._port_param}')
            logger.error('{}'.format(e))
            try:
                self.init()
            except AX25DeviceFAIL:
                logger.error(f'Port {self.port_id}: Error. Reinit Failed !! {self._port_param}')
                raise AX25DeviceFAIL


class TNC_EMU_TCP_CL(AX25Port):
    def __init__(self, port_id: int, port_handler):
        super().__init__(port_id, port_handler)
        self.tnc_protocol = Kiss(self._port_cfg)
        if self.is_multi_ch_slave():
            if self.multi_ch_tnc.init_multi_channel_tnc():
                return
            AX25DeviceFAIL(self)
        try:
            self.init()
        except AX25DeviceFAIL:
            # raise AX25DeviceFAIL(self)  # TODO in PortINIT
            AX25DeviceFAIL(self)

    def init(self):
        if self._loop_is_running:
            logger.info(f'Port {self.port_id}: TNC-EMU-TCP-CLIENT INIT')
            self.tnc_protocol.is_enabled = True
            self.tnc_protocol.set_param = False

            try:
                self.device = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except PermissionError as e:
                logger.error(f'Port {self.port_id}:Error. Cant connect to KISS TCP Device {self._port_param}')
                logger.error('{}'.format(e))
                self._loop_is_running = False
                self.device = None
                raise AX25DeviceFAIL

            except (OSError, ConnectionError) as e:
                logger.error(f'Port {self.port_id}: Error. Cant open TNC-EMU Device {self._port_param}')
                logger.error('{}'.format(e))
                self.close_device()
                raise AX25DeviceFAIL
            else:
                self.device_is_running = True
            """
               try:
                   self.device.settimeout(sock_timeout)
                   self.device.connect(self._port_param)
                   self.device_is_running = True
            """
            """
            except ConnectionRefusedError as e:
                logger.error(f'Port {self.port_id}: Error. Cant open TNC-EMU Device {self._port_param}')
                logger.error('{}'.format(e))
                raise AX25DeviceFAIL
            """


    def __del__(self):
        self.close_device()

    def close_device(self):
        self._loop_is_running = False
        if self.device is None:
            self.device_is_running = False
            return
        try:
            # Deactivate KISS Mode on TNC
            """
            if self.kiss.is_enabled:
                self.device.sendall(self.kiss.device_kiss_end())
            """
            # self.device.shutdown(socket.SHUT_RDWR)
            # if self._tnc_emu_connection is not None:
            #     self._tnc_emu_connection.close()
            self.device.close()
        except (OSError, ConnectionRefusedError, ConnectionError, AttributeError) as e:
            logger.error(f"Port {self.port_id}: Error while closing Port !")
            logger.error(f"Port {self.port_id}: {e}")
            self.device_is_running = False
            if self.device is not None:
                try:
                    self.device.close()
                except (OSError, ConnectionRefusedError, ConnectionError, AttributeError) as e:
                    logger.error(f"Port {self.port_id}: Error while closing Port !")
                    logger.error(f"Port {self.port_id}: {e}")
                    return
        finally:
            self.device_is_running = False
            if self.device is not None:
                self.device.close()

    def set_kiss_parm(self):
        if self.tnc_protocol.protocol_name != 'KISS':
            return
        if self.tnc_protocol.is_enabled and self.device is not None and self.device_is_running and self.tnc_protocol.set_param:
            kiss_cmd = self.tnc_protocol.set_all_parameter()
            if not kiss_cmd:
                return
            try:
                self.device.sendall(self.tnc_protocol.set_all_parameter())
            except (OSError, ConnectionRefusedError, ConnectionError, socket.timeout) as e:
                logger.error(f"Port {self.port_id}: SetKiss Failed !! {e}")
                logger.error('{}'.format(e))
                raise AX25DeviceFAIL

    def _rx(self):
        #self.port_w_dog = time.time()
        recv_buff = b''
        if self._tnc_emu_connection is None:
            try:
                self.device.connect(self._port_param)
            except ConnectionRefusedError:
                time.sleep(2)
                return None
            except OSError:
                logger.info(f'Port {self.port_id}: TNC-EMU Device: Closing Server connection')
                self.device.close()
                time.sleep(1)
                try:
                    self.init()
                except AX25DeviceFAIL:
                    self.device_is_running = False
                    logger.error(f'Port {self.port_id}: Error. Reinit Failed !! {self._port_param}')
                    raise AX25DeviceFAIL
                return None

            self._tnc_emu_connection, self._tnc_emu_client_address = self.device, tuple(self._port_param)
            logger.info(
                f'Port {self.port_id}: TNC-EMU Device: Server connection accepted. {self._tnc_emu_client_address}')
            self.device.settimeout(0.4)
            kiss_start_cmd = self.tnc_protocol.device_start()
            if all((self.tnc_protocol.is_enabled, kiss_start_cmd, self.tnc_protocol.set_param)):
                try:
                    self.device.sendall(kiss_start_cmd)
                except BrokenPipeError as e:
                    logger.error(f'Port {self.port_id}: {e}')
                    self.close_device()
                    raise AX25DeviceFAIL
                else:
                    try:
                        self.set_kiss_parm()
                    except AX25DeviceFAIL as e:
                        raise e


        while self._loop_is_running and self.device_is_running:
            try:
                recv_buff += self.device.recv(1)
            except socket.timeout:
                # if not recv_buff:
                return None
            except ConnectionError as e:
                logger.error(f"TNC CL : ConnectionError: {e}")
                return None
            except OSError:
                try:
                    self.device.connect(self._port_param)
                except OSError as e:
                    self._tnc_emu_connection = None
                    raise AX25DeviceERROR(e, self)

            if recv_buff:
                de_kiss_fr = self.tnc_protocol.decode_tnc_multi_ch(recv_buff)
                if de_kiss_fr is not None:
                    ret = RxBuf()
                    ret.raw_data = bytes(de_kiss_fr)
                    ret.kiss_frame = bytes(recv_buff)
                    return ret
                if self.tnc_protocol.unknown_kiss_frame(recv_buff):
                    recv_buff = b''

            else:
                if self._tnc_emu_connection is not None:
                    logger.info(f'Port {self.port_id}: TNC-EMU Device: Closing Server connection')
                    # self._tnc_emu_connection.close()
                    self._tnc_emu_connection = None
                return None
        return None

    def _tx_device(self, frame, tnc_channel=0):
        try:
            self.device.sendall(self.tnc_protocol.encode_tnc(frame.data_bytes, tnc_channel))
        except (ConnectionRefusedError, ConnectionError, BrokenPipeError) as e:
            logger.warning(
                f'Port {self.port_id}: Error. TNC-EMU Device. Try Reinit Device {self._port_param}')
            logger.warning('{}'.format(e))
            try:
                self.device.connect(self._port_param)
            except (ConnectionAbortedError, ConnectionRefusedError):
                self.init()
            except AX25DeviceFAIL:
                logger.error(f'Port {self.port_id}: Error. Reinit Failed !! {self._port_param}')
                raise AX25DeviceFAIL
        except (OSError, socket.timeout) as e:
            logger.error(
                f'Port {self.port_id}: Error. Cant send Packet to TNC-EMU Device. Try Reinit Device {self._port_param}')
            logger.error('{}'.format(e))
            try:
                self.init()
            except AX25DeviceFAIL:
                logger.error(f'Port {self.port_id}: Error. Reinit Failed !! {self._port_param}')
                raise AX25DeviceFAIL
