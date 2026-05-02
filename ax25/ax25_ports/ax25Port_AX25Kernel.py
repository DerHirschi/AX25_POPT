import socket

from ax25.ax25Error import AX25DeviceFAIL, AX25DeviceERROR
from ax25.ax25_l2.ax25Kiss import Kiss
from .ax25Port import AX25Port
from .ax25Port_Classes import RxBuf
from cfg.logger_config import logger


class AX25KernelDEV(AX25Port):
    def __init__(self, port_id: int, port_handler):
        super().__init__(port_id, port_handler)
        self.tnc_protocol = Kiss(self._port_cfg)
        try:
            self.init()
        except AX25DeviceFAIL:
            # raise AX25DeviceFAIL(self)  # TODO in PortINIT
            AX25DeviceFAIL(self)

    def init(self):
        if self._loop_is_running:
            # print("KISS TCP INIT")
            logger.info(f'Port {self.port_id}: AX25-Kernel INIT')
            sock_timeout = 0.2
            ETH_P_ALL = 3
            try:
                self.device = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
            except PermissionError as e:
                logger.error(f'Port {self.port_id}:Error. Cant connect to KISS TCP Device {self._port_param}')
                logger.error('{}'.format(e))
                self._loop_is_running = False
                self.device = None
                raise AX25DeviceFAIL
            try:
                self.device.bind((self._port_param[0], 0))
                self.device.settimeout(sock_timeout)
                self.device_is_running = True

            except (OSError, ConnectionRefusedError, ConnectionError) as e:
                logger.error(f'Port {self.port_id}:Error. Cant connect to KISS TCP Device {self._port_param}')
                logger.error('{}'.format(e))
                self.close_device()
                raise AX25DeviceFAIL

            else:
                if all((self.tnc_protocol.is_enabled, self.tnc_protocol.set_param)):
                    self.set_kiss_parm()
                return


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
        if self.tnc_protocol.is_enabled and self.device is not None and self.device_is_running:
            try:
                frame = self.tnc_protocol.set_all_parameter_ax25kernel()
                for el in frame:
                    self.device.sendall(el)
            except (OSError, ConnectionRefusedError, ConnectionError, socket.timeout) as e:
                logger.error(f"Port {self.port_id}: SetKiss Failed !! {e}")
                logger.error('{}'.format(e))
                raise AX25DeviceFAIL

    def _rx(self):
        #self.port_w_dog = time.time()
        try:
            recv_buff = self.device.recv(999)
        except socket.timeout:
            return None
        except OSError as e:
            raise AX25DeviceERROR(e, self)

        if recv_buff:
            de_kiss_fr = self.tnc_protocol.de_kiss_ax25kernel(recv_buff)
            if de_kiss_fr is not None:
                ret = RxBuf()
                ret.raw_data = bytes(de_kiss_fr)
                ret.kiss_frame = bytes(recv_buff)
                return ret
            if self.tnc_protocol.unknown_kiss_frame(recv_buff):
                return None
            return None
        else:
            return None

    def _tx_device(self, frame, tnc_channel=0):
        try:
            self.device.sendall(self.tnc_protocol.kiss_ax25kernel(frame.data_bytes))
        except (OSError, ConnectionRefusedError, ConnectionError, socket.timeout) as e:
            logger.error(f'Port {self.port_id}: Error. Cant send Packet to KISS TCP Device. Try Reinit Device {self._port_param}')
            logger.error('{}'.format(e))
            try:
                self.init()
            except AX25DeviceFAIL:
                logger.error(f'Port {self.port_id}: Error. Reinit Failed !! {self._port_param}')
                raise AX25DeviceFAIL
