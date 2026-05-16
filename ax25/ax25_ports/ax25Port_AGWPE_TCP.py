import socket

from ax25.ax25Error import AX25DeviceFAIL, AX25DeviceERROR
from ax25.ax25_l2.ax25AGWPE import AGWPEHandler
from .ax25Port import AX25Port
from .ax25Port_Classes import RxBuf
from cfg.logger_config import logger


class AGWPE_TCP(AX25Port):
    def __init__(self, port_id: int, port_handler):
        super().__init__(port_id, port_handler)
        self.tnc_protocol = AGWPEHandler(self._port_cfg)
        try:
            self.init()
        except AX25DeviceFAIL:
            # raise AX25DeviceFAIL(self)  # TODO in PortINIT
            AX25DeviceFAIL(self)

    def init(self):
        if self._loop_is_running:
            # print("KISS TCP INIT")
            logger.info(f'Port {self.port_id}: AGWPE TCP INIT')
            sock_timeout = 0.2
            # self.kiss = b'\x00'
            self.device = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            try:
                self.device.settimeout(sock_timeout)
                self.device.connect(self._port_param)
                self.device_is_running = True

            except Exception as e:
                logger.error(f'Port {self.port_id}:Error. Cant connect to AGWPE TCP Device {self._port_param}')
                logger.error('{}'.format(e))
                self.close_device()
                raise AX25DeviceFAIL

            start_seq = self.tnc_protocol.device_start()

            for start_cmd in start_seq:
                try:
                    self.device.sendall(start_cmd)
                    # print(self.device.recv(999))
                except Exception as e:
                    logger.error(f'Port {self.port_id}: {e}')
                    self.close_device()
                    raise AX25DeviceFAIL
                try:
                    recv_buff = self.device.recv(999)
                    self.tnc_protocol.decode_tnc(recv_buff)
                except socket.timeout:
                    pass
                except Exception as e:
                    raise AX25DeviceERROR(e, self)
            logger.info(f'Port {self.port_id}: AGWPE TCP INIT Done...')


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
            self.device.shutdown(socket.SHUT_RDWR)
            self.device.close()
        except Exception as e:
            logger.error(f"Port {self.port_id}: Error while closing Port !")
            logger.error(f"Port {self.port_id}: {e}")
            self.device_is_running = False
            if self.device is not None:
                try:
                    self.device.close()
                except Exception as e:
                    logger.error(f"Port {self.port_id}: Error while closing Port !")
                    logger.error(f"Port {self.port_id}: {e}")

        finally:
            self.device_is_running = False
            if self.device is not None:
                self.device.close()
            # print("KISS TCP FINALLY")
        #self.ende = True

    def _rx(self):
        #self.port_w_dog = time.time()
        try:
            recv_buff = self.device.recv(999)
        except socket.timeout:
            return None
        except Exception as e:
            raise AX25DeviceERROR(e, self)

        if recv_buff:
            #print(recv_buff)
            de_kiss_fr = self.tnc_protocol.decode_tnc(recv_buff)
            if de_kiss_fr is not None:
                ret = RxBuf()
                ret.raw_data   = bytes(de_kiss_fr)
                ret.kiss_frame = bytes(recv_buff)
                return ret
            #if self.tnc_protocol.unknown_kiss_frame(recv_buff):
            #    return None
            return None
        else:
            return None

    def _tx_device(self, frame, tnc_channel=0):
        try:
            self.device.sendall(self.tnc_protocol.encode_tnc(frame.data_bytes))
            # self.device.sendall(b'\xC0' + b'\x00' + frame.bytes + b'\xC0')
        except Exception as e:
            logger.error(f'Port {self.port_id}: Error. Cant send Packet to KISS TCP Device. Try Reinit Device {self._port_param}')
            logger.error('{}'.format(e))
            try:
                self.init()
            except Exception as e:
                logger.error(f'Port {self.port_id}: Error. Reinit Failed !! {self._port_param}')
                logger.error(f"Port {self.port_id}: Error: {e}")
                raise AX25DeviceFAIL
        # else:
        #     self._mh.bw_mon_inp(frame, self.port_id)

        ############################################
