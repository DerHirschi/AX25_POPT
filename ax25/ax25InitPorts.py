import time
import threading
from UserDB.UserDBmain import USER_DB
from ax25.ax25Statistics import MH_LIST
from ax25aprs.aprs_station import APRS_ais
from config_station import init_dir_struct, get_all_stat_cfg, logger, PortConfigInit
from ax25.ax25Port import KissTCP, KISSSerial, AXIP
from classes import RxEchoVars


class AX25PortHandler(object):
    def __init__(self):
        logger.info("Port Init.")
        init_dir_struct()

        #################
        self.is_running = True
        self.max_ports = 20
        self.ax25types = {
            'KISSTCP': KissTCP,
            'KISSSER': KISSSerial,
            'AXIP': AXIP,
        }
        ###########################
        # VArs for gathering Stuff
        # self.aprs_ais = None
        self.aprs_ais = None
        self.gui = None
        # self.ch_echo: {int:  [AX25Conn]} = {}
        self.multicast_ip_s = []        # [axip-addresses('ip', port)]
        self.all_connections = {}       # {int: AX25Conn} Channel Index
        self.link_connections = {}      # {str: AX25Conn} UID Index
        self.rx_echo: {int:  RxEchoVars} = {}
        self.beacons = {}
        self.ax25_stations_settings = get_all_stat_cfg()
        self.ax25_port_settings = {}    # Port settings are in Port .. TODO Cleanup
        self.ax25_ports = {}
        #######################################################
        # Init Ports/Devices with Config and running as Thread
        logger.info(f"Port Init Max-Ports: {self.max_ports}")
        for port_id in range(self.max_ports):       # Max Ports
            self.init_port(port_id=port_id)
        #######################################################
        # APRS AIS Thread
        self.init_aprs_ais()

    def __del__(self):
        self.close_all_ports()
        # logger.info("Ende PoPT Ver.: {}".format(VER))

    #####################
    # Setting/Parameter Updates
    def update_digi_setting(self):
        for port_kk in self.ax25_ports.keys():
            port = self.ax25_ports[port_kk]
            new_digi_calls = []
            for stat_key in port.my_stations:
                if self.ax25_stations_settings[stat_key].stat_parm_is_StupidDigi:
                    new_digi_calls.append(stat_key)
            self.ax25_ports[port_kk].port_cfg.parm_StupidDigi_calls = new_digi_calls
            self.ax25_ports[port_kk].stupid_digi_calls = new_digi_calls     # Same Object !!

    ######################
    # Port Handling
    def get_port_by_index(self, index: int):
        if index in self.ax25_ports.keys():
            return self.ax25_ports[index]
        return False

    def close_all(self):
        for k in list(self.all_connections.keys()):
            del self.all_connections[k]
        self.close_all_ports()
        if self.gui is not None:
            tmp = self.gui
            self.gui = None
            self.set_gui()
            tmp.main_win.quit()
            tmp.main_win.destroy()
        MH_LIST.save_mh_data()
        USER_DB.save_data()

    def close_aprs_ais(self):
        if self.aprs_ais is None:
            return False
        self.aprs_ais.ais_close()
        # self.aprs_ais.save_conf_to_file()
        del self.aprs_ais
        self.aprs_ais = None
        return True

    def close_all_ports(self):
        self.close_aprs_ais()
        if self.is_running:
            self.is_running = False
            for k in list(self.ax25_ports.keys()):
                self.close_port(k)

    def close_port(self, port_id: int):
        logger.info('Info: Versuche Port {} zu schließen.'.format(port_id))
        if port_id in self.ax25_ports.keys():
            port = self.ax25_ports[port_id]
            port.close()
            c = 0
            while not port.ende:
                # time.sleep(0.3)   # !! Lockt den Thread !!
                print("Warte auf Port " + str(port_id))
                logger.debug("Warte auf Port " + str(port_id))
                port.close()
                c += 1
                if c == 2:
                    break

            del self.ax25_ports[port_id]
        if port_id in self.ax25_port_settings.keys():
            del self.ax25_port_settings[port_id]
        if port_id in self.beacons.keys():
            del self.beacons[port_id]
        if port_id in self.rx_echo.keys():
            del self.rx_echo[port_id]
        del port
        self.sysmsg_to_gui('Info: Port {} erfolgreich geschlossen.'.format(port_id))
        logger.info('Info: Port {} erfolgreich geschlossen.'.format(port_id))

    def reinit_all_ports(self):
        logger.info("Reinit all Ports")
        for port_id in list(self.ax25_ports.keys()):
            self.close_port(port_id=port_id)
        time.sleep(1)  # Cooldown for Device
        for port_id in range(self.max_ports):  # Max Ports
            self.init_port(port_id=port_id)

    def reinit_port(self, port_id: int):    # Not used !!!!
        if port_id in self.ax25_ports.keys():
            self.close_port(port_id=port_id)
            time.sleep(1)  # Cooldown for Device
            self.init_port(port_id=port_id)
            self.set_gui()

    def set_kiss_param_all_ports(self):
        for port_id in list(self.ax25_ports.keys()):
            if self.ax25_ports[port_id].kiss.is_enabled:
                self.ax25_ports[port_id].set_kiss_parm()
                self.sysmsg_to_gui('Hinweis: Kiss-Parameter an TNC auf Port {} gesendet..'.format(port_id))

    def init_port(self, port_id: int):
        logger.info("Initialisiere Port: {}".format(port_id))
        if port_id in self.ax25_ports.keys():
            logger.error('Could not initialise Port {}. Port already in use'.format(port_id))
            self.sysmsg_to_gui('Error: Port {} konnte nicht initialisiert werden. Port wird bereits benutzt.'
                               .format(port_id))
        else:
            ##########
            # Init CFG
            cfg = PortConfigInit(loaded_stat=self.ax25_stations_settings, port_id=port_id)
            if cfg.parm_PortTyp:
                #########################
                # Init Port/Device
                temp = self.ax25types[cfg.parm_PortTyp](cfg, self)
                if not temp.device_is_running:
                    logger.error('Could not initialise Port {}'.format(cfg.parm_PortNr))
                    self.sysmsg_to_gui('Error: Port {} konnte nicht initialisiert werden.'.format(cfg.parm_PortNr))
                ##########
                # Beacons
                for stat in temp.port_cfg.parm_beacons.keys():
                    be_list = temp.port_cfg.parm_beacons[stat]
                    for beacon in be_list:
                        beacon.re_init()
                self.beacons[port_id] = temp.port_cfg.parm_beacons
                ##########################
                # Start Port/Device Thread
                temp.start()
                ######################################
                # Gather all Ports in dict: ax25_ports
                temp.gui = self.gui
                self.ax25_ports[port_id] = temp
                self.ax25_port_settings[port_id] = temp.port_cfg
                self.rx_echo[port_id] = RxEchoVars(port_id)
                self.sysmsg_to_gui('Info: Port {} erfolgreich initialisiert.'.format(cfg.parm_PortNr))
                logger.info("Port {} Typ: {} erfolgreich initialisiert.".format(port_id, temp.port_typ))

    def init_aprs_ais(self):
        self.aprs_ais = APRS_ais()
        if self.aprs_ais is not None:
            self.aprs_ais.port_handler = self
            if self.aprs_ais.ais is not None:
                # self.aprs_ais.loop_is_running = True
                threading.Thread(target=self.aprs_ais.ais_rx_task).start()

    def save_all_port_cfgs(self):
        for port_id in self.ax25_ports.keys():
            self.ax25_ports[port_id].port_cfg.save_to_pickl()

    ######################
    # GUI Handling
    def set_gui(self, gui=None):
        """ PreInit: Set GUI Var """
        if gui is not None:
            self.gui = gui
        for k in self.ax25_ports.keys():
            self.ax25_ports[k].gui = self.gui

    def sysmsg_to_gui(self, msg: str = ''):
        if self.gui is not None and self.is_running:
            self.gui.msg_to_monitor(msg)

    ######################
    # Connection Handling
    def insert_conn2all_conn_var(self, new_conn, ind: int = 1):
        # if not new_conn.is_link:
        keys = list(self.all_connections.keys())
        if keys:
            tr = False
            # Check if Connection is already in all_conn...
            for k in list(self.all_connections.keys()):
                if new_conn == self.all_connections[k]:
                    tr = True
                    if new_conn.ch_index != k:
                        logger.warning("Channel Index != Real Index !!!")
                        new_conn.ch_index = int(k)
            if not tr:
                while True:
                    if ind in keys:
                        ind += 1
                    else:
                        new_conn.ch_index = int(ind)
                        self.all_connections[ind] = new_conn
                        break
        else:
            new_conn.ch_index = int(ind)
            self.all_connections[ind] = new_conn
        if self.gui is not None:
            self.gui.ch_status_update()

    """
    def cleanup_conn2all_conn_var(self):
        temp = []
        for k in list(self.all_connections.keys()):
            # conn: AX25Conn = self.all_connections[k]
            conn = self.all_connections[k]
            if conn.zustand_exec.stat_index in [0]:
                temp.append(k)
        for k in temp:
            # conn: AX25Conn = self.all_connections[k]
            conn = self.all_connections[k]
            conn.ch_index = 0
            del self.all_connections[k]
    """

    def del_conn2all_conn_var(self, conn):
        for k in list(self.all_connections.keys()):
            # temp_conn: AX25Conn = self.all_connections[k]
            if self.all_connections[k] == conn:
                if self.gui is not None:
                    self.gui.send_to_qso(data=f'\n*** Disconnected from {str(conn.to_call_str)}\n', ch_index=int(conn.ch_index))
                    self.gui.disco_sound()
                self.all_connections[k].ch_index = 0
                del self.all_connections[k]

        if self.gui is not None:
            self.gui.ch_status_update()

    def del_link(self, uid: str):
        if uid in self.link_connections.keys():
            del self.link_connections[uid]

    def new_outgoing_connection(self,               # NICE ..
                                dest_call: str,
                                own_call: str,
                                via_calls=None,     # Auto lookup in MH if not exclusive Mode
                                port_id=-1,         # -1 Auto lookup in MH list
                                axip_add=('', 0),   # AXIP Adress
                                exclusive=False,    # True = no lookup in MH list
                                link_conn=None,     # Linked Connection AX25Conn
                                channel=1           # Channel/Connection Index = Channel-ID
                                ):
        """ Handels New Outgoing Connections for CLI and LINKS """
        # Incoming Parameter Check
        if via_calls is None:
            via_calls = []
        if link_conn and not via_calls:
            return False, 'Error: Link No Via Call'
        if not dest_call or not own_call:
            return False, 'Error: Invalid Call'
        mh_entry = MH_LIST.mh_get_data_fm_call(dest_call)
        if not exclusive:
            if mh_entry:
                # port_id = int(mh_entry.port_id)
                via_calls += min(list(mh_entry.all_routes), key=len)
                axip_add = tuple(mh_entry.axip_add)

        if not axip_add[0] and mh_entry:
            axip_add = tuple(mh_entry.axip_add)
        if port_id == -1 and mh_entry:
            port_id = int(mh_entry.port_id)
        if port_id not in self.ax25_ports.keys():
            return False, 'Error: Invalid Port'
        if self.ax25_ports[port_id].port_typ == 'AXIP':
            if not mh_entry.axip_add[0]:
                return False, 'Error: No AXIP Address'
        if link_conn and not via_calls:
            return False, 'Error: Link No Via Call'

        connection = self.ax25_ports[port_id].build_new_connection(own_call=own_call,
                                                                   dest_call=dest_call,
                                                                   via_calls=via_calls,
                                                                   axip_add=axip_add,
                                                                   link_conn=link_conn)
        """
        print('------------- InitPorts ---------------')
        print(f'conn: {connection}')
        print(f'dest_call: {dest_call}')
        print(f'own_call: {own_call}')
        print(f'via_calls: {via_calls}')
        print(f'link_conn: {link_conn}')
        """

        if connection:
            self.insert_conn2all_conn_var(new_conn=connection, ind=channel)   # TODO . ? IF Link CH 11 +
            # connection.link_connection(link_conn) # !!!!!!!!!!!!!!!!!
            user_db_ent = USER_DB.get_entry(dest_call, add_new=False)
            if user_db_ent:
                if user_db_ent.Name:
                    return True, f'\r*** Link Setup to {dest_call} - ({user_db_ent.Name})> Port {port_id}\r'
            return True, f'\r*** Link Setup to {dest_call} > Port {port_id}\r'
        return False, '\r*** Busy'

    ######################
    # RX-ECHO Handling
    def rx_echo_input(self, ax_frame, port_id):
        from_call = ax_frame.from_call.call_str
        for k in self.rx_echo.keys():
            rx_echo_var: RxEchoVars = self.rx_echo[k]
            if port_id != rx_echo_var.port_id:
                for port in list(rx_echo_var.rx_ports):
                    if rx_echo_var.rx_ports[port]:
                        if from_call in rx_echo_var.rx_ports[port]:
                            if k in self.rx_echo[port].tx_ports.keys():
                                rx_echo_var.tx_buff.append(ax_frame)
                    else:
                        if k in self.rx_echo[port].tx_ports.keys():
                            rx_echo_var.tx_buff.append(ax_frame)

    ######################
    # Pipe-Tool
    def get_all_pipes(self):
        ret = []
        for port_id in self.ax25_ports.keys():
            for pipe_uid in self.ax25_ports[port_id].pipes.keys():
                ret.append(self.ax25_ports[port_id].pipes[pipe_uid])
        return ret

    ######################
    # FT
    def get_all_ft_query(self):
        # conn.ft_tx_queue: [FileTX]
        # conn.ft_tx_activ: FileTX
        res = {}
        for ch_id in self.all_connections:
            conn = self.all_connections[ch_id]
            tmp = conn.ft_queue
            if conn.ft_obj is not None:
                tmp = [conn.ft_obj] + tmp
            if tmp:
                res[ch_id] = tmp
        return res

    def get_aprs_ais(self):
        return self.aprs_ais

    def get_all_ports(self):
        return self.ax25_ports

    def get_all_connections(self):
        return self.all_connections

    def get_stat_calls_fm_port(self, port_id=0):
        if port_id in self.ax25_ports.keys():
            return self.ax25_ports[port_id].my_stations
        return []
    """
    def debug_fnc(self):
        print("--Port")
        self.deb_port = dict(show_mem_size(self.ax25_ports, previous_sizes=dict(self.deb_port)))
        for p_id in self.ax25_ports:
            self.ax25_ports[p_id].debug_show_var_size()

        print()
        print("--Conn")
        self.deb_conn = dict(show_mem_size(self.all_connections, previous_sizes=dict(self.deb_conn)))
        print()
        print("--InitPorts.self")
        self.deb_self = dict(show_mem_size(self.__dict__, previous_sizes=dict(self.deb_self)))
        print()

        print("--MH")
        self.deb_mh = dict(show_mem_size(self.mh.__dict__, previous_sizes=dict(self.deb_mh)))
        print()

        print("--Globals")
        self.deb_glbs = dict(show_mem_size(globals(),previous_sizes=dict(self.deb_glbs)))
    """


PORT_HANDLER = AX25PortHandler()
