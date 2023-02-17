import copy
import socket
import serial
import threading
import time
import crcmod

import ax25.ax25Statistics
from ax25.ax25InitPorts import AX25Conn
from ax25.ax25dec_enc import AX25Frame, DecodingERROR, Call, reverse_uid, bytearray2hexstr
import ax25.ax25monitor as ax25monitor
import logging

logger = logging.getLogger(__name__)
crc_x25 = crcmod.predefined.mkCrcFun('x-25')


class AX25DeviceERROR(Exception):
    logger.error('AX25DeviceERROR Error !')


class AX25DeviceFAIL(Exception):
    logger.error('AX25DeviceFAIL while try Sending Data !')


class AX25Port(threading.Thread):
    def __init__(self, station_cfg):
        super(AX25Port, self).__init__()
        print("PORT INIT")
        """ self.ax25_port_handler will be set in AX25PortInit """
        self.ax25_ports: {int: AX25Port}
        self.ax25_ports_handler: ax25.ax25InitPorts.AX25PortHandler
        # self.mh_list: ax25.ax25Statistics.MH
        ############
        # CONFIG
        # self.device = None
        self.station_cfg = station_cfg
        self.port_param = self.station_cfg.parm_PortParm
        self.portname = self.station_cfg.parm_PortName
        self.my_stations = self.station_cfg.parm_StationCalls
        self.is_stupid_digi = self.station_cfg.parm_is_StupidDigi
        self.is_smart_digi = self.station_cfg.parm_isSmartDigi
        self.parm_TXD = self.station_cfg.parm_TXD
        self.TXD = time.time()
        self.digi_buf: [AX25Frame] = []
        # CONFIG ENDE
        #############
        #############
        # VARS
        self.loop_is_running = False
        #############
        self.monitor = ax25monitor.Monitor()
        self.MYHEARD = self.station_cfg.glb_mh
        self.port_hndl = self.station_cfg.glb_port_handler
        # self.gui = self.station_cfg.glb_gui
        self.gui = None
        self.is_gui = False
        self.connections: {str: AX25Conn} = {}
        self.device = None
        try:
            self.init()
        except AX25DeviceFAIL as e:
            raise e
        """
        self.dw_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        try:
            self.dw_sock.connect(self.address)
            self.dw_sock.settimeout(sock_timeout)
        except (OSError, ConnectionRefusedError, ConnectionError) as e:
            logger.error('Error. Cant connect to Direwolf {}'.format(self.address))
            logger.error('{}'.format(e))
            raise e
        """
    def set_gui(self, gui):
        if self.gui is None:
            self.gui = gui
            self.is_gui = True


    def init(self):
        pass

    def __del__(self):
        self.loop_is_running = False

    def rx(self):
        return b''

    def tx(self, frame: AX25Frame):
        pass

    def set_TXD(self):
        self.TXD = time.time() + self.parm_TXD / 1000

    def rx_pac_handler(self, ax25_frame: AX25Frame):
        """ Not Happy with that Part . . :-( TODO Cleanup """
        cfg = self.station_cfg()
        # Monitor
        if self.is_gui:
            self.gui.update_monitor(self.monitor.frame_inp(ax25_frame, self.portname), conf=cfg,
                                       tx=False)
        # self.monitor.frame_inp(ax25_frame, self.portname)
        # MH List and Statistics
        self.MYHEARD.mh_inp(ax25_frame, self.portname)
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

            self.connections[uid] = AX25Conn(ax25_frame, cfg)
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
                            cfg = self.station_cfg()
                            # Incoming REQ
                            conn_in = AX25Conn(ax25_frame, cfg)
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
                                    conn_out = AX25Conn(copy_ax25frame, cfg, rx=False)
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
                    except AX25DeviceFAIL as e:
                        raise e
                    # self.connections[k].tx_buf_2send = self.connections[k].tx_buf_2send[1:]
                    # Monitor
                    # self.monitor.frame_inp(el, 'DW-TX')
                    cfg = self.station_cfg()
                    # Monitor
                    if self.is_gui:
                        self.gui.update_monitor(self.monitor.frame_inp(el, self.portname), conf=cfg, tx=True)
        # DIGI
        fr: AX25Frame
        for fr in self.digi_buf:
            try:
                self.tx(frame=fr)
            except AX25DeviceFAIL as e:
                raise e
            # Monitor
            # self.monitor.frame_inp(fr, self.portname)
            cfg = self.station_cfg()
            # Monitor
            if self.is_gui:
                self.gui.update_monitor(self.monitor.frame_inp(fr, self.portname), conf=cfg, tx=True)
        self.digi_buf = []

    def cron_pac_handler(self):
        """ Execute Cronjob on all Connections"""
        for k in self.connections.keys():
            conn: AX25Conn = self.connections[k]
            conn.exec_cron()

    def new_connection(self, ax25_frame: AX25Frame):
        """ New Outgoing Connection """
        cfg = self.station_cfg()
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

        conn = AX25Conn(ax25_frame, cfg, rx=False)
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
                self.run_once()
                time.sleep(0.1)

    def run_once(self):
        while self.loop_is_running:
            try:
                ##############################################
                buf = self.rx()
                ##############################################
                logger.debug('Inp Buf> {}'.format(buf))
            except AX25DeviceERROR:
                break

            if buf:  # RX ############
                self.set_TXD()
                ax25frame = AX25Frame()
                e = None
                try:
                    # Decoding
                    ax25frame.decode(buf)
                except DecodingERROR as e:
                    logger.error('{}.decoding: {}'.format(self.portname, e))
                    break
                if e is None and ax25frame.validate():
                    # ######### RX #############
                    # Handling
                    self.rx_pac_handler(ax25frame)
                    # Pseudo Full Duplex for AXIP.
                    if self.station_cfg.parm_full_duplex:
                        break
            else:
                break
        if time.time() > self.TXD:
            #############################################
            # Crone
            self.cron_pac_handler()
            # ######### TX #############
            # TX
            self.tx_pac_handler()

        ############################
        ############################
        # Cleanup
        self.del_connections()


class KissTCP(AX25Port):

    def init(self):
        print("KISS TCP INIT")
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
            recv_buff = self.device.recv(400)
        except socket.timeout:
            # self.device.close()
            raise AX25DeviceERROR
        if recv_buff[:2] == b'\xc0\x00' and recv_buff[-1:] == b'\xc0':
            return recv_buff[2:-1]
        return b''

    def tx(self, frame: AX25Frame):
        ############################################
        out = (bytes.fromhex('c000') + frame.hexstr + bytes.fromhex('c0'))
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
                if recv_buff:
                    # print(recv_buff)
                    if len(recv_buff) > 14:  # ? Min Pack Len 17
                        if recv_buff[:2] == b'\xc0\x00' and recv_buff[-1:] == b'\xc0':
                            return recv_buff[2:-1]
                else:
                    return b''

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


class AXIPClient(AX25Port):

    def init(self):
        print("AXIP Client INIT")
        sock_timeout = 0.5
        self.device = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.device.settimeout(sock_timeout)

    def __del__(self):
        self.loop_is_running = False
        if self.device is not None:
            try:
                self.device.close()
            except socket.error:
                pass

    def rx(self):
        try:
            recv_buff = self.device.recv(400)
        except socket.error:
            raise AX25DeviceERROR
        ###################################
        # CRC
        crc = recv_buff[-2:]
        crc = int(bytearray2hexstr(crc[::-1]), 16)
        pack = recv_buff[:-2]
        calc_crc = crc_x25(pack)
        ###################################
        if calc_crc == crc:
            return pack
        return b''

    def tx(self, frame: AX25Frame):
        ###################################
        # CRC
        calc_crc = crc_x25(frame.hexstr)
        calc_crc = bytes.fromhex(hex(calc_crc)[2:].zfill(4))[::-1]
        ###################################
        try:
            self.device.sendto(frame.hexstr + calc_crc, self.port_param)
        except (OSError, ConnectionRefusedError, ConnectionError, socket.timeout, socket.error) as e:
            logger.error('Error. Cant send Packet to AXIP Device. Try Reinit Device {}'.format(self.port_param))
            logger.error('{}'.format(e))
            try:
                self.init()
            except AX25DeviceFAIL:
                logger.error('Error. Reinit AXIP Failed !! {}'.format(self.port_param))
                raise AX25DeviceFAIL
