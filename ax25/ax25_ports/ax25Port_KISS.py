import socket
import time

import serial

from ax25.ax25Error import AX25DeviceFAIL, AX25DeviceERROR
from ax25.ax25_l2.ax25Kiss import Kiss
from .ax25Port import AX25Port
from .ax25Port_Classes import RxBuf
from cfg.logger_config import logger
from fnc.os_fnc import is_linux


class KISSSerial(AX25Port):
    def __init__(self, port_id: int, popt_handler):
        super().__init__(port_id, popt_handler)
        self.tnc_protocol = Kiss(self._port_cfg)
        if self.is_multi_ch_slave():
            self.init_multi_ch_slave()

        try:
            self.init()
        except AX25DeviceFAIL:
            # raise AX25DeviceFAIL(self)  # TODO in PortINIT
            AX25DeviceFAIL(self)


    def init(self):
        if self._loop_is_running:
            logger.info(self._logTag + "KISS Serial INIT")
            try:

                self.device = serial.Serial(self._port_param[0],
                                            self._port_param[1],
                                            timeout=0.4,
                                            #write_timeout=0.3
                                            #dsrdtr=self._port_cfg.get('parm_serial_dtr',      True),
                                            #rtscts=self._port_cfg.get('parm_serial_rts',      True),
                                            #xonxoff= self._port_cfg.get('parm_serial_xonxoff',False)
                                            )
                if not is_linux():
                    self.device.dtr      = self._port_cfg.get('parm_serial_dtr',    True)
                    self.device.rts      = self._port_cfg.get('parm_serial_rts',    True)
                    self.device.xonxoff  = self._port_cfg.get('parm_serial_xonxoff',False)
                #self.device.dtr = True
                #self.device.rts = True
                #self.device.xonxoff = False
                #self.device.parity   = self._port_cfg.get('parm_serial_parity', False)
                #self.device.stopbits = self._port_cfg.get('parm_serial_stopBit', 1)
                """
                True
                True
                False
                N
                1
                """
                #print(self.device.dtr)
                #print(self.device.rts)
                #print(self.device.xonxoff)
                #print(self.device.parity)
                #print(self.device.stopbits)
                """
                PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE = 'N', 'E', 'O', 'M', 'S'
                STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO = (1, 1.5, 2)
                FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS = (5, 6, 7, 8)
                
                PARITY_NAMES = {
                    PARITY_NONE: 'None',
                    PARITY_EVEN: 'Even',
                    PARITY_ODD: 'Odd',
                    PARITY_MARK: 'Mark',
                    PARITY_SPACE: 'Space',
                }
                """

                self.device_is_running = True
            except Exception as e:
                logger.error(self._logTag + f'Error. Cant connect to KISS Serial Device {self._port_param}')
                logger.error(e)
                self.close_device()
                raise AX25DeviceFAIL
            else:
                time.sleep(1)
                tnc_banner = self.device.readall().decode('UTF-8', 'ignore')
                logger.info(self._logTag + f"TNC-Banner: {tnc_banner}")
                kiss_start_cmd = self.tnc_protocol.device_start()
                if self.tnc_protocol.is_enabled:

                    # print(f"TNC-Banner: {tnc_banner}")
                    # self.device.flush()
                    try:
                        if kiss_start_cmd:
                            self.device.write(self.tnc_protocol.device_start())
                            logger.info(self._logTag +  f"TNC-MSG: {self.device.readall().decode('UTF-8', 'ignore')}")
                        if self.tnc_protocol.set_param:
                            self.set_kiss_parm()
                    except Exception as e:
                        logger.error(self._logTag +
                            f"Can not set Serial Device into KISS MODE")
                        logger.error(self._logTag + f"Device: {self._port_param}")
                        logger.error(e)
                        raise e

    def _reinit(self):
        self._close_dev()
        try:
            self.init()
        except Exception as e:
            logger.error(f"Port {self.port_id}: Error: {e}")
            raise AX25DeviceFAIL

    def close_device(self):
        self._close_dev()

    def _close_dev(self):
        # self._loop_is_running = False
        self._loop_is_running = False
        if self.device is None:
            self.device_is_running = False
            return
        try:
            # Deactivate KISS Mode on TNC
            if self.tnc_protocol.is_enabled:
                if self.tnc_protocol.device_end():
                    self.device.write(self.tnc_protocol.device_end())
                    time.sleep(1)


            time.sleep(1)
            if is_linux():
                if hasattr(self.device, 'readall'):
                    logger.info(self._logTag + f"TNC - REST: {self.device.readall()}")
            else:
                if hasattr(self.device, 'flush'):
                    self.device.flush()
            if hasattr(self.device, 'close'):
                self.device.close()
            # self.device_is_running = False
        except Exception as e:
            logger.warning(self._logTag + f"Error while closing: {e}")
        self.device_is_running = False
        # self.ende = True

    def set_kiss_parm(self):
        if self.tnc_protocol.protocol_name != 'KISS':
            return
        if self.tnc_protocol.is_enabled and self.device is not None:
            try:
                self.device.write(self.tnc_protocol.set_all_parameter())
            # except serial.portNotOpenError:
            except Exception as e:
                logger.error(f"Port {self.port_id}: SetKiss Failed !! {e}")
                self.device_is_running = False
                self.close_device()
                raise AX25DeviceFAIL

    def _rx(self):
        recv_buff = bytearray()
        while self._loop_is_running and self.device_is_running:
            #self.port_w_dog = time.time()
            try:
                recv_buff += self.device.read()
            except serial.SerialException:
                # There is no new data from serial port
                if not recv_buff:
                    return None
            except Exception as e:
                logger.warning(f'Port {self.port_id}: Serial Device Error {e}')
                try:
                    # self.init()
                    self._reinit()
                    return None
                except Exception as e:
                    self.close_device()
                    logger.error(f"Port {self.port_id}: Reinit Failed !! {self._port_param}")
                    logger.error(f"Port {self.port_id}: Error: {e}")
                    raise AX25DeviceERROR

            if recv_buff:
                de_kiss_fr, tnc_channel = self.tnc_protocol.decode_tnc_multi_ch(recv_buff)
                if de_kiss_fr is not None:
                    ret = RxBuf()
                    ret.raw_data    = bytes(de_kiss_fr)
                    ret.kiss_frame  = bytes(recv_buff)
                    ret.tnc_channel = int(tnc_channel)
                    return ret
                if self.tnc_protocol.unknown_kiss_frame(recv_buff):
                    return None

            else:
                return None
        return None

    def _tx_device(self, frame, tnc_channel=0):
        if self.device is None:
            try:
                # self.init()
                self._reinit()
            except Exception as e:
                logger.error(f'Port {self.port_id}: Error. Reinit Failed !! {self._port_param}')
                logger.error(f"Port {self.port_id}: Error: {e}")
                self.close_device()
                raise AX25DeviceERROR
        if self.device is None:
            logger.error(f'Port {self.port_id}: Error. Reinit Failed !! {self._port_param}')
            self.close_device()
            raise AX25DeviceERROR

        try:
            self.device.write(self.tnc_protocol.encode_tnc(frame.data_bytes, tnc_channel))
        except Exception as e:
            logger.warning(
                f'Port {self.port_id}: Error. Cant send Packet to KISS Serial Device. Try Reinit Device {self._port_param}')
            logger.warning('{}'.format(e))
            try:
                # self.init()
                self._reinit()
            except Exception as e:
                logger.error(f'Port {self.port_id}: Error. Reinit Failed !! {self._port_param}')
                logger.error(f"Port {self.port_id}: Error: {e}")
                self.close_device()
                raise AX25DeviceERROR


class KissTCP(AX25Port):
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
            # print("KISS TCP INIT")
            logger.info(f'Port {self.port_id}: KISS TCP INIT')
            sock_timeout = 0.2
            # self.kiss = b'\x00'
            self.device = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            try:
                self.device.settimeout(sock_timeout)
                self.device.connect(self._port_param)
                self.device_is_running = True

            except Exception as e:
                logger.error(f'Port {self.port_id}:Error. Cant connect to KISS TCP Device {self._port_param}')
                logger.error('{}'.format(e))
                self.close_device()
                raise AX25DeviceFAIL

            else:
                start_cmd = self.tnc_protocol.device_start()
                if self.tnc_protocol.is_enabled:
                    if start_cmd:
                        try:
                            self.device.sendall(start_cmd)
                            # print(self.device.recv(999))
                        except Exception as e:
                            logger.error(f'Port {self.port_id}: {e}')
                            self.close_device()
                            raise AX25DeviceFAIL
                    if self.tnc_protocol.set_param:
                        try:
                            self.set_kiss_parm()
                        except Exception as e:
                            raise e

    def __del__(self):
        # self.device.shutdown(socket.SHUT_RDWR)
        #self.close_device()
        pass

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

    def set_kiss_parm(self):
        if self.tnc_protocol.protocol_name != 'KISS':
            return
        if self.tnc_protocol.is_enabled and self.device is not None and self.device_is_running:

            try:
                self.device.sendall(self.tnc_protocol.set_all_parameter())
            except Exception as e:
                logger.error(f"Port {self.port_id}: SetKiss Failed !! {e}")
                logger.error('{}'.format(e))
                raise AX25DeviceFAIL

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
            de_kiss_fr, tnc_channel = self.tnc_protocol.decode_tnc_multi_ch(recv_buff)
            if de_kiss_fr is not None:
                ret = RxBuf()
                ret.raw_data    = bytes(de_kiss_fr)
                ret.kiss_frame  = bytes(recv_buff)
                ret.tnc_channel = int(tnc_channel)
                return ret
            if self.tnc_protocol.unknown_kiss_frame(recv_buff):
                return None
            return None
        else:
            return None

    def _tx_device(self, frame, tnc_channel=0):
        try:
            self.device.sendall(self.tnc_protocol.encode_tnc(frame.data_bytes, tnc_channel))
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
