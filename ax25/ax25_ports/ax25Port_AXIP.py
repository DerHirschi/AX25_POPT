import socket

from ax25 import crc_x25
from ax25.ax25Error import AX25DeviceFAIL, MCastInitError, AX25DeviceERROR
from ax25.ax25_l2.ax25Kiss import Kiss
from ax25.ax25_l2.ax25dec_enc import bytearray2hexstr
from .ax25Port import AX25Port
from .ax25Port_Classes import RxBuf
from cfg.logger_config import logger
from fnc.socket_fnc import get_ip_by_hostname


class AXIP(AX25Port):
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
            # print("AXIP Client INIT")
            logger.info(f"Port {self.port_id}: AXIP Client INIT")
            if not self._port_param[0]:
                hostname = socket.gethostname()
                self._port_param = socket.gethostbyname(hostname), self._port_param[1]
            own_ipAddr = self._port_param[0]
            logger.info(f"Port {self.port_id}: AXIP bind on IP: {own_ipAddr}")
            # sock_timeout = 0.1

            self.device = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            # self.device.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.device.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024 * 1024)
            self.device.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024)
            # self.device.settimeout(1)
            self.device.setblocking(False)  # Nicht-blockierend
            try:
                self.device.bind(self._port_param)
            except Exception as e:
                logger.error(f"Port {self.port_id}: Error {e}")
                # self.device.shutdown(socket.SHUT_RDWR)
                # self.device.close()
                # self.device_is_running = False
                self.close_device()
                raise AX25DeviceFAIL

            self.device_is_running = True
            # MCast
            if self._port_cfg.get('parm_axip_Multicast', False):
                logger.info(f"Port {self.port_id}: Set Multicast to Server !!")
                self._mcast_server = self._popt_handler.get_mcast_server()
                if hasattr(self._mcast_server, 'set_mcast_port'):
                    try:
                        self._mcast_server.set_mcast_port(self)
                    except MCastInitError:
                        # self._mcast_server = None
                        logger.error(f"Port {self.port_id}: Set Multicast Server failed !!")

    def close_device(self):
        # self._mcast_server = None
        self._loop_is_running = False
        if self.device is None:
            self.device_is_running = False
            return
        try:
            # print("Try Close AXIP")
            logger.info(f"Port {self.port_id}: Try Close AXIP")
            self.device.close()
        except Exception as e:
            logger.error(f"Port {self.port_id}: Close AXIP except: {e}")
            # print(f"Try Close AXIP except: {e}")
        finally:
            self.device_is_running = False
            if self.device is not None:
                self.device.close()
            # print("AXIP FINALLY")
            logger.info(f"Port {self.port_id}: Close AXIP done")

    def _rx(self):
        #self.port_w_dog = time.time()
        try:
            udp_recv = self.device.recvfrom(800)
            recv_buff = udp_recv[0]
            to_call_ip_addr = udp_recv[1]
            ###################################
            # CRC
            crc = recv_buff[-2:]
            crc = int(bytearray2hexstr(crc[::-1]), 16)
            pack = recv_buff[:-2]
            calc_crc = crc_x25(pack)
            ret = RxBuf()
            ret.axip_add = to_call_ip_addr
            if calc_crc == crc:
                ret.raw_data = pack
                ret.kiss_frame = b''
            return ret
        except BlockingIOError:
            return RxBuf()  # Keine Daten verfügbar
        except Exception as e:
            logger.error(f"Port {self.port_id}: Error in _rx: {e}")
            return RxBuf()

    def _tx_device(self, frame, multicast=True):
        if not hasattr(frame, 'axip_add'):
            return
        if not frame.axip_add:
            return
        if frame.axip_add == ('', 0):
            return
        axip_add = get_ip_by_hostname(frame.axip_add[0])    # TODO Each Frame Hostname Request ?? Performance !!
        if not axip_add:
            return
        if axip_add:
            frame.axip_add = (axip_add, int(frame.axip_add[1]))
        ###################################
        # CRC
        calc_crc = crc_x25(frame.data_bytes)
        calc_crc = bytes.fromhex(hex(calc_crc)[2:].zfill(4))[::-1]
        ###################################
        try:
            self.device.sendto(frame.data_bytes + calc_crc, frame.axip_add)
            # self.device.settimeout(0.1)
        except (ConnectionRefusedError, ConnectionError, socket.timeout, socket.error) as e:
            logger.warning(f"Port {self.port_id}: Error. Cant send Packet to AXIP Device. Try Reinit Device {frame.axip_add}")
            logger.warning('{}'.format(e))
            try:
                self.init()
            except AX25DeviceFAIL:
                logger.error(f"Port {self.port_id}: Error. Reinit AXIP Failed !! {self._port_param}")
                raise AX25DeviceFAIL
        except OSError:
            pass
        except TypeError as e:
            logger.error(f"Port {self.port_id}: TypeError AXIP Dev !!! \n {e}")
            logger.error(frame.axip_add)
            logger.error(frame.data_bytes + calc_crc)
        """
        if all((
                hasattr(self._mcast_server, 'mcast_tx'),
                multicast
               )):
            self._mcast_server.mcast_tx(ax25frame=frame)
        """

    def tx_multicast(self, frame):
        try:
            self._tx_device(frame, multicast=False)
        except AX25DeviceERROR as e:
            logger.error(f"Port {self.port_id}: AX25DeviceERROR tx_multicast()")
            self.close()
            raise e
    """
    def clean_anti_spam(self):
        for k in list(self.axip_anti_spam.keys()):
            if self.axip_anti_spam[k][1] < time.time():
                del self.axip_anti_spam[k]
    """
