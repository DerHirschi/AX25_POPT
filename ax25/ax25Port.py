import copy
import socket
import serial
import threading
import time
from datetime import datetime
import crcmod

# mport main
from ax25.ax25Connection import AX25Conn
from ax25.ax25dec_enc import AX25Frame, reverse_uid, bytearray2hexstr
from ax25.ax25Error import AX25EncodingERROR, AX25DecodingERROR, AX25DeviceERROR, AX25DeviceFAIL, logger
import ax25.ax25monitor as ax25monitor
# import logging

# logger = logging.getLogger(__name__)
crc_x25 = crcmod.predefined.mkCrcFun('x-25')


class RxBuf:
    axip_add = '', 0
    raw_data = b''


class Beacon:
    def __init__(self, ax25_frame: AX25Frame, port_id: int, repeat_time: int, move_time: int, aprs: bool = False):
        self.port_id = port_id
        self.ax_frame = ax25_frame
        self.repeat_time = repeat_time
        self.move_time = move_time
        self.cooldown = time.time()
        self.next_run = int(datetime.now().strftime("%M")) + move_time
        self.is_enabled = True
        self.ax_frame.ctl_byte.UIcByte()
        self.ax_frame.pid_byte.text()
        self.aprs = aprs

        self.ax_frame.ctl_byte.cmd = self.aprs

        self.ax_frame.encode()
        self.from_call = ax25_frame.from_call.call_str
        self.to_call = ax25_frame.to_call.call_str


class AX25Port(threading.Thread):
    def __init__(self, port_cfg, port_handler):
        super(AX25Port, self).__init__()

        """ self.ax25_port_handler will be set in AX25PortInit """
        self.ax25_ports: {int: AX25Port}
        # self.ax25_ports_handler: ax25.ax25InitPorts.AX25PortHandler
        ############
        # CONFIG
        self.port_cfg = port_cfg
        self.port_handler = port_handler
        self.mh = port_handler.mh
        self.port_cfg.mh = self.mh

        self.port_param = self.port_cfg.parm_PortParm
        self.portname = self.port_cfg.parm_PortName
        self.port_typ = self.port_cfg.parm_PortTyp
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
        self.loop_is_running = False
        self.monitor = ax25monitor.Monitor()
        # self.port_hndl = self.port_cfg.glb_port_handler
        self.gui = None
        self.is_gui = False
        self.connections: {str: AX25Conn} = {}
        self.device = None
        self.beacons_list: [Beacon] = []
        ##############
        # Beacon TEST
        test_beacon_fr = AX25Frame()
        test_beacon_fr.from_call.call = 'MD7TES'
        test_beacon_fr.to_call.call = 'TEST'
        test_beacon_fr.data = b'=== TEST Beacon ==='
        test_beacon = Beacon(test_beacon_fr, self.port_cfg.parm_PortNr, 2, 0)
        self.beacons_list.append(test_beacon)
        # AXIP VARs
        self.own_ipAddr = ''
        # self.to_call_ip_addr = ('', 0)
        try:
            self.init()
        except AX25DeviceFAIL as e:
            raise e

    def set_gui(self, gui):
        # if self.gui is None:
        self.gui = gui
        self.is_gui = True

    def init(self):
        pass

    def __del__(self):
        self.close()
        # self.loop_is_running = False

    def close(self):
        for conn in self.connections:
            # Try to send a Disc
            conn.zustand_exec.change_state(4)
            conn.zustand_exec.tx(None)
        time.sleep(1)
        self.loop_is_running = False

    def rx(self):
        return RxBuf()

    def tx(self, frame: AX25Frame):
        pass

    def set_TXD(self):
        self.TXD = time.time() + self.parm_TXD / 1000

    def rx_pac_handler(self, ax25_frame: AX25Frame):
        """ Not Happy with that Part . . :-( TODO Cleanup """
        cfg = self.port_cfg
        # Monitor
        if self.is_gui:
            self.gui.update_monitor(self.monitor.frame_inp(ax25_frame, self.portname), conf=cfg,
                                       tx=False)
        # self.monitor.frame_inp(ax25_frame, self.portname)
        # MH List and Statistics
        # self.mh.mh_inp(ax25_frame, self.portname)
        self.mh.mh_inp(ax25_frame, self.portname)
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

            self.connections[uid] = AX25Conn(ax25_frame, cfg, port=self)
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
                            cfg = self.port_cfg
                            # Incoming REQ
                            conn_in = AX25Conn(ax25_frame, cfg, self)
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
                                    print("Same UID in Connections.. Try change SSID {}".format(copy_ax25frame.addr_uid))
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
                                    conn_out = AX25Conn(copy_ax25frame, cfg, port=self, rx=False)
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
                    except AX25EncodingERROR:
                        pass
                    cfg = self.port_cfg
                    # Monitor
                    if self.is_gui:
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
            except AX25EncodingERROR:
                logger.error('Encoding Error: ! MSG to short !')
            # Monitor
            cfg = self.port_cfg
            # Monitor
            if self.is_gui:
                self.gui.update_monitor(self.monitor.frame_inp(fr, self.portname), conf=cfg, tx=True)
        self.digi_buf = []
        return tr

    def cron_pac_handler(self):
        """ Execute Cronjob on all Connections"""
        for k in self.connections.keys():
            conn: AX25Conn = self.connections[k]
            conn.exec_cron()

    def cron_port_handler(self):
        """ Execute Port related Cronjob like Beacon sending"""
        self.send_beacons()

    def send_beacons(self):
        # TODO to all AXIP Clients
        for beacon in self.beacons_list:
            if time.time() > beacon.cooldown:
                now = datetime.now()
                now_min = int(now.strftime("%M"))
                if now_min == beacon.next_run + beacon.move_time:
                    beacon.next_run = beacon.repeat_time + now_min
                    if beacon.next_run > 59:
                        beacon.next_run -= 60
                    beacon.cooldown = time.time() + 60
                    self.tx(beacon.ax_frame)
                    # Monitor
                    cfg = self.port_cfg
                    if self.is_gui:
                        self.gui.update_monitor(self.monitor.frame_inp(beacon.ax_frame, self.portname), conf=cfg, tx=True)

    def new_connection(self, ax25_frame: AX25Frame):
        """ New Outgoing Connection """
        cfg = self.port_cfg
        ax25_frame.encode()
        # print("Same UID ?? --  {}".format(ax25_frame.addr_uid))
        # print("Same UID connections?? --  {}".format(self.connections.keys()))
        # ax25_frame.addr_uid = reverse_uid(ax25_frame.addr_uid)
        while ax25_frame.addr_uid in self.connections.keys() or\
                reverse_uid(ax25_frame.addr_uid) in self.connections.keys():
            print("Same UID !! {}".format(ax25_frame.addr_uid))
            ax25_frame.from_call.call_str = ''
            ax25_frame.from_call.ssid += 1
            ax25_frame.from_call.enc_call()
            if ax25_frame.from_call.ssid > 15:
                return False
            ax25_frame.encode()
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
        if not self.loop_is_running:
            self.loop_is_running = True
            while self.loop_is_running:
                self.tasks()
                time.sleep(0.1)

    def tasks(self):
        while self.loop_is_running:
            try:
                ##############################################
                buf: RxBuf = self.rx()
                ##############################################
                logger.debug('Inp Buf> {}'.format(buf))
            except AX25DeviceERROR:
                break

            if buf.raw_data:  # RX ############
                self.set_TXD()
                ax25frame = AX25Frame()
                ax25frame.axip_add = buf.axip_add
                e = None
                try:
                    # Decoding
                    ax25frame.decode(buf.raw_data)
                except AX25DecodingERROR:
                    logger.error('Port:{} decoding: '.format(self.portname))
                    logger.error('{}: org {}'.format(self.portname, buf.raw_data))
                    logger.error('{}: hex {}'.format(self.portname, bytearray2hexstr(buf.raw_data)))
                    break
                if e is None and ax25frame.validate():
                    # ######### RX #############
                    # Handling
                    self.rx_pac_handler(ax25frame)
                    # Pseudo Full Duplex for AXIP.
                    if self.port_cfg.parm_full_duplex:
                        break
            else:
                break
        if time.time() > self.TXD:
            #############################################
            # Crone
            self.cron_pac_handler()
            # ######### TX #############
            # TX
            block_tx = self.tx_pac_handler()
            if not block_tx:
                self.cron_port_handler()

        ############################
        ############################
        # Cleanup
        self.del_connections()


class KissTCP(AX25Port):

    def init(self):
        print("KISS TCP INIT")
        logger.info("KISS TCP INIT")
        sock_timeout = 0.5
        self.device = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        try:
            self.device.connect(self.port_param)
            self.device.settimeout(sock_timeout)
        except (OSError, ConnectionRefusedError, ConnectionError) as e:
            logger.error('Error. Cant connect to KISS TCP Device {}'.format(self.port_param))
            logger.error('{}'.format(e))
            raise AX25DeviceFAIL

    def __del__(self):
        self.loop_is_running = False
        if self.device is not None:
            try:
                self.device.close()
            except (OSError, ConnectionRefusedError, ConnectionError):
                pass

    def rx(self):
        try:
            recv_buff = self.device.recv(3000)
        except socket.timeout:
            # self.device.close()
            raise AX25DeviceERROR
        ret = RxBuf()
        if recv_buff[:2] == b'\xc0\x00' and recv_buff[-1:] == b'\xc0':
            ret.raw_data = recv_buff[2:-1]
        return ret

    def tx(self, frame: AX25Frame):
        ############################################
        # !!!!!!! BUG ?????????
        out = (bytes.fromhex('c000') + frame.hexstr + bytes.fromhex('c0'))
        if len(out) < 15:
            logger.error('Error Port {0} - Packet < 15 - \nout: {1}\nframe.hexstr: {2}'.format(
                self.port_param,
                out,
                frame.hexstr))
            raise AX25EncodingERROR(frame)
        # Just Log it and let it through. DW is block this
        #######################################
        try:
            self.device.sendall(out)
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
        print("KISS Serial INIT")
        logger.info("KISS Serial INIT")
        try:
            self.device = serial.Serial(self.port_param[0], self.port_param[1], timeout=0.5)
        except (FileNotFoundError, serial.serialutil.SerialException) as e:
            logger.error('Error. Cant connect to KISS Serial Device {}'.format(self.port_param))
            logger.error('{}'.format(e))
            raise AX25DeviceFAIL

    def __del__(self):
        self.loop_is_running = False
        if self.device is not None:
            try:
                self.device.close()
            except (FileNotFoundError, serial.serialutil.SerialException):
                pass

    def rx(self):
        recv_buff = b''
        while True:
            try:
                recv_buff += self.device.read()
            except serial.SerialException:
                # There is no new data from serial port
                return b''
            except TypeError as e:
                # Disconnect of USB->UART occured
                logger.error('Serial Device Error {}'.format(e))
                # self.device.close()
                try:
                    self.init()
                except AX25DeviceFAIL:
                    logger.error('Error. Reinit Failed !! {}'.format(self.port_param))
                    raise AX25DeviceFAIL
            else:
                ret = RxBuf()
                if recv_buff:
                    # print(recv_buff)
                    if len(recv_buff) > 14:  # ? Min Pack Len 17
                        if recv_buff[:2] == b'\xc0\x00' and recv_buff[-1:] == b'\xc0':
                            ret.raw_data = recv_buff[2:-1]
                return ret

    def tx(self, frame: AX25Frame):
        try:
            self.device.write(bytes.fromhex('c000') + frame.hexstr + bytes.fromhex('c0'))
        except (FileNotFoundError, serial.serialutil.SerialException) as e:
            logger.error('Error. Cant send Packet to KISS Serial Device. Try Reinit Device {}'.format(self.port_param))
            logger.error('{}'.format(e))
            try:
                self.init()
            except AX25DeviceFAIL:
                logger.error('Error. Reinit Failed !! {}'.format(self.port_param))
                raise AX25DeviceFAIL


class AXIP(AX25Port):

    def init(self):
        print("AXIP Client INIT")
        logger.info("AXIP Client INIT")
        if not self.port_param[0]:
            hostname = socket.gethostname()
            self.port_param = socket.gethostbyname(hostname), self.port_param[1]
        self.own_ipAddr = self.port_param[0]
        print(self.own_ipAddr)
        sock_timeout = 0.5
        self.device = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.device.settimeout(sock_timeout)
        self.device.bind(self.port_param)

    def __del__(self):
        self.loop_is_running = False
        if self.device is not None:
            try:
                self.device.close()
            except socket.error:
                pass

    def rx(self):
        try:
            udp_recv = self.device.recvfrom(800)
        except socket.error:
            raise AX25DeviceERROR
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
        return ret

    def tx(self, frame: AX25Frame):
        ###################################
        # CRC
        calc_crc = crc_x25(frame.hexstr)
        calc_crc = bytes.fromhex(hex(calc_crc)[2:].zfill(4))[::-1]
        ###################################
        try:
            self.device.sendto(frame.hexstr + calc_crc, frame.axip_add)
        except (OSError, ConnectionRefusedError, ConnectionError, socket.timeout, socket.error) as e:
            logger.error('Error. Cant send Packet to AXIP Device. Try Reinit Device {}'.format(frame.axip_add))
            logger.error('{}'.format(e))
            try:
                self.init()
            except AX25DeviceFAIL:
                logger.error('Error. Reinit AXIP Failed !! {}'.format(self.port_param))
                raise AX25DeviceFAIL
