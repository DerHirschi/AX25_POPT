import copy
import socket
import serial
import threading
import time
import crcmod

from ax25.ax25Beacon import Beacon
# mport main
from ax25.ax25Kiss import Kiss
from ax25.ax25Connection import AX25Conn
from ax25.ax25dec_enc import AX25Frame, reverse_uid, bytearray2hexstr, de_arschloch_kiss_frame, arschloch_kiss_frame
from ax25.ax25Error import AX25EncodingERROR, AX25DecodingERROR, AX25DeviceERROR, AX25DeviceFAIL, logger
import ax25.ax25monitor as ax25monitor

# import logging

# logger = logging.getLogger(__name__)
crc_x25 = crcmod.predefined.mkCrcFun('x-25')


class RxBuf:
    axip_add = '', 0
    raw_data = b''
    kiss = b''


class AX25Port(threading.Thread):
    def __init__(self, port_cfg, port_handler):
        super(AX25Port, self).__init__()

        self.ende = False
        self.device_is_running = False
        self.loop_is_running = True
        """ self.ax25_port_handler will be set in AX25PortInit """
        self.ax25_ports: {int: AX25Port}
        # self.ax25_ports_handler: ax25.ax25InitPorts.AX25PortHandler
        ############
        # CONFIG
        self.port_cfg = port_cfg
        self.port_handler = port_handler
        self.mh = port_handler.mh
        self.beacons = self.port_handler.beacons
        self.kiss = Kiss(self.port_cfg)
        # self.port_cfg.mh = self.mh  # ?????

        self.port_param = self.port_cfg.parm_PortParm
        self.portname = self.port_cfg.parm_PortName
        self.port_typ = self.port_cfg.parm_PortTyp
        self.port_id = self.port_cfg.parm_PortNr
        self.my_stations = self.port_cfg.parm_StationCalls
        self.is_stupid_digi = self.port_cfg.parm_is_StupidDigi
        self.is_smart_digi = self.port_cfg.parm_isSmartDigi
        self.parm_TXD = self.port_cfg.parm_TXD
        self.TXD = time.time()
        self.digi_buf: [AX25Frame] = []
        # CONFIG ENDE
        #############
        #############
        # VARS
        self.monitor = ax25monitor.Monitor()
        # self.port_hndl = self.port_cfg.glb_port_handler
        self.gui = None
        self.is_gui = False
        self.connections: {str: AX25Conn} = {}
        self.device = None
        ##############
        # Beacon TEST
        """
        test_beacon_fr = AX25Frame()
        test_beacon_fr.from_call.call = 'MD7TES'
        test_beacon_fr.to_call.call = 'TEST'
        test_beacon_fr.data = b'=== TEST Beacon ==='
        test_beacon = Beacon(test_beacon_fr, self.port_cfg.parm_PortNr, 2, 0)
        self.beacons_list.append(test_beacon)
        """
        # AXIP VARs
        self.own_ipAddr = ''
        self.axip_anti_spam = {}
        # self.to_call_ip_addr = ('', 0)
        try:
            self.init()
        except AX25DeviceFAIL as e:
            raise e

    def set_gui(self, gui):
        # if self.gui is None:
        self.gui = gui
        if self.gui is None:
            self.is_gui = False
        else:
            self.is_gui = True

    def init(self):
        pass

    def __del__(self):
        self.close()
        # self.loop_is_running = False

    def set_kiss_parm(self):
        pass

    def close_device(self):
        pass

    def close(self):
        """
        for k in self.connections.keys():
            conn: AX25Conn = self.connections[k]
            # Try to send a Disc
            conn.zustand_exec.change_state(4)
            conn.zustand_exec.tx(None)
        time.sleep(1)
        """
        # self.loop_is_running = False
        self.close_device()
        # if self.device is not None:
        # self.device.close()

        """
        if self.device is not None:
            self.device.close()
            self.device = None
        """

    def rx(self):
        return RxBuf()

    def tx(self, frame: AX25Frame):
        pass

    def tx_multicast(self, frame: AX25Frame):
        pass

    def set_TXD(self):
        self.TXD = time.time() + self.parm_TXD / 1000

    def rx_pac_handler(self, ax25_frame: AX25Frame):
        """ Not Happy with that Part . . :-( TODO Cleanup or AGAIN !! """
        # cfg = self.port_cfg
        # Monitor
        if self.is_gui:
            self.gui.update_monitor(self.monitor.frame_inp(ax25_frame, self.portname), conf=self.port_cfg,
                                    tx=False)
        # MH List and Statistics
        self.mh.mh_inp(ax25_frame, self.portname)
        # RX-ECHO
        self.rx_echo(ax25_frame=ax25_frame)
        # Existing Connections
        uid = str(ax25_frame.addr_uid)
        if uid in self.connections.keys():
            # Connection already established
            if ax25_frame.is_digipeated:
                self.connections[uid].set_T2()
                self.connections[uid].handle_rx(ax25_frame=ax25_frame)
            else:
                my_digi_call = self.connections[uid].my_digi_call
                if my_digi_call:
                    if ax25_frame.digi_check_and_encode(call=my_digi_call, h_bit_enc=False):
                        if uid in self.connections.keys():
                            self.connections[uid].set_T2()
                            print("KEY:{} - {} -{}".format(ax25_frame.addr_uid, uid, self.connections.keys()))
                            self.connections[uid].handle_rx(ax25_frame=ax25_frame)

        # New Incoming Connection Request
        elif ax25_frame.to_call.call_str in self.my_stations \
                and ax25_frame.is_digipeated:

            self.connections[uid] = AX25Conn(ax25_frame, cfg=self.port_cfg, port=self)
            self.connections[uid].set_T2()
            self.connections[uid].handle_rx(ax25_frame=ax25_frame)
        # DIGI / LINK Connection
        elif reverse_uid(uid) in self.connections.keys():
            uid = reverse_uid(uid)
            my_digi_call = self.connections[uid].my_digi_call
            if my_digi_call:
                if ax25_frame.digi_check_and_encode(call=my_digi_call, h_bit_enc=False):
                    if uid in self.connections.keys():
                        self.connections[uid].set_T2()
                        self.connections[uid].handle_rx(ax25_frame=ax25_frame)

        # DIGI
        elif self.is_stupid_digi or self.is_smart_digi:
            for my_call in self.my_stations:
                # Simple "Stupid" DIGI
                if self.is_stupid_digi:
                    if ax25_frame.digi_check_and_encode(call=my_call, h_bit_enc=True):
                        self.digi_buf.append(ax25_frame)
                else:
                    # DIGI UI Frames
                    if ax25_frame.ctl_byte.flag == 'UI':
                        if ax25_frame.digi_check_and_encode(call=my_call, h_bit_enc=True):
                            self.digi_buf.append(ax25_frame)
                    else:
                        # New "Smart" Digi / Link Request
                        if ax25_frame.digi_check_and_encode(call=my_call, h_bit_enc=False):
                            print("NEW DIGI CONN")
                            # "Smart" DIGI
                            # Incoming REQ
                            conn_in = AX25Conn(ax25_frame, self.port_cfg, self)
                            conn_in.my_digi_call = str(my_call)
                            conn_in.is_link = True
                            conn_in.set_T2()
                            conn_in.handle_rx(ax25_frame=ax25_frame)
                            self.connections[uid] = conn_in
                            # TODO Irgendwo hier ist ein Käfer ... Glaube ich ..
                            if conn_in.zustand_exec.stat_index == 5:  # Accept ( Incoming SABM )
                                # Init Outgoing Connection
                                print("CONN IN UID: {}".format(uid))
                                print("CONN IN MyCall: {}".format(conn_in.my_digi_call))
                                copy_ax25frame = copy.copy(ax25_frame)
                                copy_ax25frame.short_via_calls(call=my_call)
                                copy_ax25frame.encode()

                                while copy_ax25frame.addr_uid in self.connections.keys() or \
                                        reverse_uid(copy_ax25frame.addr_uid) in self.connections.keys():
                                    print(
                                        "Same UID in Connections.. Try change SSID {}".format(copy_ax25frame.addr_uid))
                                    my_call = copy_ax25frame.increment_viacall_ssid(call=my_call)
                                    if my_call:
                                        copy_ax25frame.short_via_calls(call=my_call)
                                        print("New MyCall {}".format(my_call))
                                        copy_ax25frame.digi_check_and_encode(call=my_call, h_bit_enc=True)
                                        print("New UID  {}".format(copy_ax25frame.addr_uid))
                                        # copy_ax25frame.short_via_calls(call=my_call)
                                        # copy_ax25frame.encode(digi=True)
                                    else:
                                        conn_in.zustand_exec.change_state(4)
                                        break
                                if conn_in.zustand_exec.stat_index == 5:
                                    conn_out = AX25Conn(copy_ax25frame, self.port_cfg, port=self, rx=False)
                                    conn_out_uid = conn_out.ax25_out_frame.addr_uid
                                    conn_out.my_digi_call = str(my_call)
                                    print("CONN OUT UID: {}".format(conn_out_uid))
                                    print("CONN OUT MyCall: {}".format(conn_out.my_digi_call))
                                    # Link Connections together
                                    conn_out.link_connection(conn_in)
                                    conn_in.link_connection(conn_out)
                                    conn_in.tx_buf_rawData = conn_out.rx_buf_rawData
                                    conn_out.tx_buf_rawData = conn_in.rx_buf_rawData

                                    conn_out.zustand_exec.__init__(conn_out)
                                    conn_in.zustand_exec.__init__(conn_in)  # Reinit
                                    if self.is_gui:
                                        self.gui.ch_btn_status_update()
                                    self.connections[str(conn_out_uid)] = conn_out

    def tx_pac_handler(self):
        tr = False
        for k in self.connections.keys():
            conn: AX25Conn = self.connections[k]
            if time.time() > conn.t2:
                snd_buf = list(conn.tx_buf_ctl) + list(conn.tx_buf_2send)
                conn.tx_buf_ctl = []
                conn.tx_buf_2send = []
                conn.REJ_is_set = False
                el: AX25Frame
                for el in snd_buf:
                    # el.kiss = self.kiss
                    if conn.my_digi_call:
                        print("Send DIGI CALL: " + conn.my_digi_call)
                        el.set_check_h_bits(dec=False)
                        el.digi_check_and_encode(call=conn.my_digi_call, h_bit_enc=True)
                        el.encode(digi=True)  # Why encoding again ?? But it works.
                    else:
                        el.encode()

                    try:
                        self.tx(frame=el)
                        tr = True
                    except AX25DeviceFAIL as e:
                        raise e

                    cfg = self.port_cfg
                    # Monitor
                    if self.gui is not None:
                        self.gui.update_monitor(self.monitor.frame_inp(el, self.portname), conf=cfg, tx=True)
            else:
                tr = True
        # DIGI
        fr: AX25Frame
        for fr in self.digi_buf:
            try:
                self.tx(frame=fr)
                tr = True
            except AX25DeviceFAIL as e:
                raise e

            # Monitor
            cfg = self.port_cfg
            # Monitor
            if self.is_gui:
                self.gui.update_monitor(self.monitor.frame_inp(fr, self.portname), conf=cfg, tx=True)
        self.digi_buf = []
        return tr

    def rx_echo_pac_handler(self):
        tr = False
        # RX-Echo
        fr: AX25Frame
        for fr in self.port_handler.rx_echo[self.port_id].tx_buff:
            try:
                self.tx(frame=fr)
                tr = True
            except AX25DeviceFAIL as e:
                raise e
            except AX25EncodingERROR:
                logger.error('Encoding Error: ! MSG to short !')
            # Monitor
            cfg = self.port_cfg
            # Monitor
            if self.is_gui:
                self.gui.update_monitor(
                    self.monitor.frame_inp(fr, self.portname),
                    conf=self.port_cfg,
                    tx=True)
        self.port_handler.rx_echo[self.port_id].tx_buff = []
        return tr

    def rx_echo(self, ax25_frame: AX25Frame):
        if self.is_gui:
            if self.gui.setting_rx_echo.get():
                self.port_handler.rx_echo_input(ax_frame=ax25_frame, port_id=self.port_id)

    def cron_pac_handler(self):
        """ Execute Cronjob on all Connections"""
        for k in self.connections.keys():
            conn: AX25Conn = self.connections[k]
            conn.exec_cron()

    def cron_port_handler(self):
        """ Execute Port related Cronjob like Beacon sending"""
        self.send_beacons()

    def send_beacons(self):
        # print(self.beacons)
        # print(self.beacons[self.port_id].keys())
        tr = True
        if self.gui is not None:
            if not self.gui.setting_bake.get():
                tr = False
        if tr:
            for k in self.beacons[self.port_id].keys():
                beacon_list = self.beacons[self.port_id][k]
                beacon: Beacon
                for beacon in beacon_list:
                    send_it = beacon.crone()
                    if send_it:
                        print(send_it)
                    ip_fm_mh = self.mh.mh_get_last_ip(beacon.to_call, self.port_cfg.parm_axip_fail)
                    beacon.ax_frame.axip_add = ip_fm_mh
                    if self.port_typ == 'AXIP' and not self.port_cfg.parm_axip_Multicast:
                        if ip_fm_mh == ('', 0):
                            send_it = False
                    if send_it:
                        if beacon.encode():
                            self.tx(beacon.ax_frame)
                            # Monitor
                            cfg = self.port_cfg
                            if self.is_gui:
                                self.gui.update_monitor(self.monitor.frame_inp(beacon.ax_frame, self.portname),
                                                        conf=cfg,
                                                        tx=True)

    def new_connection(self, ax25_frame: AX25Frame):
        """ New Outgoing Connection """
        cfg = self.port_cfg
        ax25_frame.encode()
        while ax25_frame.addr_uid in self.connections.keys() or \
                reverse_uid(ax25_frame.addr_uid) in self.connections.keys():
            logger.debug("Same UID !! {}".format(ax25_frame.addr_uid))
            ax25_frame.from_call.call_str = ''
            ax25_frame.from_call.ssid += 1
            try:
                ax25_frame.from_call.enc_call()
            except AX25EncodingERROR:
                return False
            if ax25_frame.from_call.ssid > 15:
                return False
            try:
                ax25_frame.encode()
            except AX25EncodingERROR:
                logger.error("AX25EncodingError: AX25Port Nr:({}): new_connection()".format(self.port_id))
                raise AX25EncodingERROR(self)
        conn = AX25Conn(ax25_frame, cfg, rx=False, port=self)
        conn.cli.change_cli_state(1)
        self.connections[ax25_frame.addr_uid] = conn
        # self.tx_pac_handler()
        return conn

    def del_connections(self):
        del_k = []
        for k in self.connections.keys():
            conn: AX25Conn = self.connections[k]
            # S0 ENDE
            if not conn.zustand_exec.stat_index:
                # And empty Buffer ?? S0 should be enough
                del_k.append(k)
        for el in del_k:
            del self.connections[el]

    def run(self):

        while self.loop_is_running and self.device_is_running:
            self.tasks()
            time.sleep(0.1)
        self.ende = True

    def tasks(self):
        while self.loop_is_running:
            try:
                ##############################################
                buf: RxBuf = self.rx()
                ##############################################
            except AX25DeviceERROR:
                break
            if buf is None:
                buf = RxBuf()
            if buf.raw_data and self.loop_is_running:  # RX ############
                logger.debug('Inp RAW Buf - Port {} > {}'.format(self.port_id, buf.raw_data))
                self.set_TXD()
                ax25frame = AX25Frame()
                ax25frame.axip_add = buf.axip_add
                # ax25frame.kiss = buf.kiss
                e = None
                try:
                    # Decoding
                    ax25frame.decode(buf.raw_data)
                except AX25DecodingERROR:
                    logger.error('Port:{} decoding: '.format(self.portname))
                    logger.error('{}: org {}'.format(self.portname, buf.raw_data))
                    logger.error('{}: hex {}'.format(self.portname, bytearray2hexstr(buf.raw_data)))
                    break
                # logger.debug('Inp fromhexstr fnc() - Port {} > {}'.format(self.port_id, ax25frame.hexstr))
                if e is None and ax25frame.validate():
                    # ######### RX #############
                    # Handling
                    self.rx_pac_handler(ax25frame)
                    # Pseudo Full Duplex for AXIP.
                    if self.port_cfg.parm_axip_Multicast:
                        self.tx_multicast(frame=ax25frame)
                    if self.port_cfg.parm_full_duplex:
                        break

            else:
                break
        if time.time() > self.TXD and self.loop_is_running:
            #############################################
            # Crone
            self.cron_pac_handler()
            # ######### TX #############
            # TX
            if not self.tx_pac_handler():           # Prio
                if not self.cron_port_handler():    # Non Prio / Beacons
                    self.rx_echo_pac_handler()      # Non non Prio / RX-ECHO

        ############################
        ############################
        # Cleanup
        self.del_connections()


class KissTCP(AX25Port):

    def init(self):
        if self.loop_is_running:
            print("KISS TCP INIT")
            logger.info("KISS TCP INIT")
            sock_timeout = 0.2
            # self.kiss = b'\x00'
            self.device = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            try:
                self.device.settimeout(sock_timeout)
                self.device.connect(self.port_param)
                self.device_is_running = True
            except (OSError, ConnectionRefusedError, ConnectionError) as e:
                logger.error('Error. Cant connect to KISS TCP Device {}'.format(self.port_param))
                logger.error('{}'.format(e))
                # self.device.shutdown(socket.SHUT_RDWR)
                self.device.close()
                # raise AX25DeviceFAIL
            else:
                if self.kiss.is_enabled:
                    self.device.sendall(self.kiss.device_kiss_start())
                    self.set_kiss_parm()

    def __del__(self):
        # self.device.shutdown(socket.SHUT_RDWR)
        self.close_device()

    def close_device(self):
        self.loop_is_running = False
        if self.device is not None:
            try:
                if self.kiss.is_enabled:
                    self.device.sendall(self.kiss.device_kiss_end())

                self.device.settimeout(0)
                # self.device.recv(999)   # ???
                self.device.shutdown(socket.SHUT_RDWR)
                self.device.close()
            except (OSError, ConnectionRefusedError, ConnectionError):
                pass

    def set_kiss_parm(self):
        if self.kiss.is_enabled:
            self.device.sendall(self.kiss.set_all_parameter())

    def rx(self):
        try:
            recv_buff = self.device.recv(999)
        except socket.timeout:
            # self.device.close()
            raise AX25DeviceERROR
        except OSError:
            raise AX25DeviceERROR
        ret = RxBuf()

        if recv_buff:
            # print(recv_buff)
            de_kiss_fr = self.kiss.de_kiss(recv_buff)
            # if recv_buff[:1] == b'\xc0' and recv_buff[-1:] == b'\xc0' and len(recv_buff) > 14:
            if de_kiss_fr:
                # ret.raw_data = recv_buff[2:-1]
                # ret.kiss = recv_buff[1:2]
                # ret.raw_data = recv_buff[2:-1]
                # ret.raw_data = de_arschloch_kiss_frame(recv_buff[2:-1])
                # self.kiss = ret.kiss
                ret.raw_data = de_kiss_fr
                # return ret
        return ret

    def tx(self, frame: AX25Frame):
        """
        if self.kiss:
            frame.hexstr = self.kiss + arschloch_kiss_frame(frame.hexstr)
        out = (bytes.fromhex('c0') + frame.hexstr + bytes.fromhex('c0'))
        """
        try:
            self.device.sendall(self.kiss.kiss(frame.bytes))
        except (OSError, ConnectionRefusedError, ConnectionError, socket.timeout) as e:
            logger.error('Error. Cant send Packet to KISS TCP Device. Try Reinit Device {}'.format(self.port_param))
            logger.error('{}'.format(e))
            try:
                self.init()
            except AX25DeviceFAIL:
                logger.error('Error. Reinit Failed !! {}'.format(self.port_param))
                raise AX25DeviceFAIL
        ############################################


class KISSSerial(AX25Port):

    def init(self):
        if self.loop_is_running:
            print("KISS Serial INIT")
            logger.info("KISS Serial INIT")
            # self.kiss = b'\x00'
            try:
                self.device = serial.Serial(self.port_param[0], self.port_param[1], timeout=0.2)
                self.device_is_running = True
            except (FileNotFoundError, serial.serialutil.SerialException) as e:
                logger.error('Error. Cant connect to KISS Serial Device {}'.format(self.port_param))
                logger.error('{}'.format(e))
                # self.device.close()
                # raise AX25DeviceFAIL
            else:
                if self.kiss.is_enabled:
                    self.device.write(self.kiss.device_kiss_start())
                    # self.device.write(b'\xc0\x10\x0c\xc0')
                    self.set_kiss_parm()

    def __del__(self):
        self.close_device()

    def close_device(self):
        self.loop_is_running = False
        if self.device is not None:
            try:
                if self.kiss.is_enabled:
                    self.device.write(self.kiss.device_kiss_end())
                self.device.close()
                self.device_is_running = False
            except (FileNotFoundError, serial.serialutil.SerialException):
                pass

    def set_kiss_parm(self):
        if self.kiss.is_enabled:
            self.device.write(self.kiss.set_all_parameter())

    def rx(self):
        recv_buff = b''
        while self.loop_is_running and self.device_is_running:
            # print('RX LOOP')
            try:
                recv_buff += self.device.read()
            except serial.SerialException as e:
                # There is no new data from serial port
                return RxBuf()
            except TypeError as e:
                # Disconnect of USB->UART occured
                logger.warning('Serial Device Error {}'.format(e))
                # self.device.close()
                try:
                    self.init()
                except AX25DeviceFAIL:
                    logger.error('Error. Reinit Failed !! {}'.format(self.port_param))
                    raise AX25DeviceFAIL
            else:
                ret = RxBuf()
                if recv_buff:
                    de_kiss_fr = self.kiss.de_kiss(recv_buff)
                    # if recv_buff[:1] == b'\xc0' and recv_buff[-1:] == b'\xc0' and len(recv_buff) > 14:
                    if de_kiss_fr:
                        # ret.raw_data = recv_buff[2:-1]
                        #ret.kiss = recv_buff[1:2]
                        # ret.raw_data = recv_buff[2:-1]
                        #ret.raw_data = de_arschloch_kiss_frame(recv_buff[2:-1])
                        # self.kiss = ret.kiss
                        ret.raw_data = de_kiss_fr
                        return ret
                return ret

    def tx(self, frame: AX25Frame):
        # frame.hexstr = self.kiss.kiss(frame.hexstr)
        try:
            self.device.write(self.kiss.kiss(frame.bytes))
        except (FileNotFoundError, serial.serialutil.SerialException) as e:
            logger.warning('Error. Cant send Packet to KISS Serial Device. Try Reinit Device {}'.format(self.port_param))
            logger.warning('{}'.format(e))
            try:
                self.init()
            except AX25DeviceFAIL:
                logger.error('Error. Reinit Failed !! {}'.format(self.port_param))
                raise AX25DeviceFAIL


class AXIP(AX25Port):

    def init(self):
        if self.loop_is_running:
            print("AXIP Client INIT")
            logger.info("AXIP Client INIT")
            if not self.port_param[0]:
                hostname = socket.gethostname()
                self.port_param = socket.gethostbyname(hostname), self.port_param[1]
            self.own_ipAddr = self.port_param[0]
            logger.info('AXIP bind on IP: {}'.format(self.own_ipAddr))
            sock_timeout = 0.2
            self.device = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.device.settimeout(sock_timeout)
            try:
                self.device.bind(self.port_param)
                self.device_is_running = True
            except OSError as e:
                logger.warning('AXIP {}'.format(e))
                # self.device.shutdown(socket.SHUT_RDWR)
                self.device.close()
                self.device = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                self.device.settimeout(sock_timeout)
                self.device_is_running = False
                try:
                    self.device.bind(self.port_param)
                    self.device_is_running = True
                except OSError as e:
                    logger.error('AXIP 2 {}'.format(e))
                    # self.device.shutdown(socket.SHUT_RDWR)
                    self.device.close()
                    self.device_is_running = False
                    # raise AX25DeviceFAIL

    def __del__(self):
        # self.device.shutdown(socket.SHUT_RDWR)
        self.close_device()

    def close_device(self):
        self.loop_is_running = False
        if self.device is not None:
            try:
                self.device.shutdown(socket.SHUT_RDWR)
                self.device.close()
                self.device.recv(999)
                time.sleep(0.5)
            except socket.error:
                pass

    def rx(self):
        try:
            udp_recv = self.device.recvfrom(800)
        # except socket.error:
        # raise AX25DeviceERROR
        except OSError:
            return RxBuf()
        else:
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
                ret.kiss = b''
            return ret

    def tx(self, frame: AX25Frame, no_multicast=False):
        # print('_____________________________')
        # print(frame.axip_add)
        # print('_____________________________')
        if frame.axip_add != ('', 0):
            ###################################
            # CRC
            calc_crc = crc_x25(frame.bytes)
            calc_crc = bytes.fromhex(hex(calc_crc)[2:].zfill(4))[::-1]
            ###################################
            try:
                self.device.sendto(frame.bytes + calc_crc, frame.axip_add)
            except (ConnectionRefusedError, ConnectionError, socket.timeout, socket.error) as e:
                logger.warning('Error. Cant send Packet to AXIP Device. Try Reinit Device {}'.format(frame.axip_add))
                logger.warning('{}'.format(e))
                try:
                    self.init()
                except AX25DeviceFAIL:
                    logger.error('Error. Reinit AXIP Failed !! {}'.format(self.port_param))
                    raise AX25DeviceFAIL
            except OSError:
                pass
        if self.port_cfg.parm_axip_Multicast and not no_multicast:
            self.tx_multicast(frame=frame)

    def tx_multicast(self, frame: AX25Frame):
        sendet = [frame.to_call.call_str]
        # self.axip_anti_spam[frame.hexstr] = [frame.axip_add], time.time()
        self.clean_anti_spam()
        all_axip_stat = self.mh.mh_get_ip_fm_all(self.port_cfg.parm_axip_fail)
        send_it = True
        for station in all_axip_stat:
            if frame.bytes in self.axip_anti_spam.keys():
                if frame.axip_add in self.axip_anti_spam[frame.bytes][0]:
                    if self.axip_anti_spam[frame.bytes][1] > time.time():
                        send_it = False
                else:
                    tmp: [] = self.axip_anti_spam[frame.bytes][0]
                    tmp.append(frame.axip_add)
                    self.axip_anti_spam[frame.bytes] = tmp, time.time() + self.port_cfg.parm_Multicast_anti_spam
            else:
                self.axip_anti_spam[frame.bytes] = [
                    frame.axip_add], time.time() + self.port_cfg.parm_Multicast_anti_spam

            if station[0] not in sendet and send_it:
                sendet.append(station[0])
                frame.axip_add = station[1]
                try:
                    self.tx(frame, no_multicast=True)
                except (ConnectionRefusedError, ConnectionError, socket.timeout):
                    self.mh.mh_ip_failed(station[0])
                except (OSError, socket.error) as e:
                    logger.error(
                        'Error. Cant send Packet to AXIP Device MULTICAST {}'.format(frame.axip_add))
                    logger.error('{}'.format(e))

    def clean_anti_spam(self):
        for k in list(self.axip_anti_spam.keys()):
            if self.axip_anti_spam[k][1] < time.time():
                del self.axip_anti_spam[k]
