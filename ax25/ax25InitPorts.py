import config_station
from ax25.ax25Port import *
from config_station import *
from gui.guiRxEchoSettings import RxEchoVars


class AX25PortHandler(object):
    def __init__(self, glb_MH):
        logger.info("Starte PoPT ...")
        config_station.init_dir_struct()
        self.is_running = True
        self.max_ports = 20
        self.ax25types = {
            'KISSTCP': KissTCP,
            'KISSSER': KISSSerial,
            'AXIP': AXIP,
        }
        ###########################
        # VArs for gathering Stuff
        # self.all_connections: {int: AX25Conn} = {}
        self.all_connections = {}
        self.mh = glb_MH
        # self.client_db = cli.ClientDB.ClientDB()
        self.gui = None
        self.rx_echo: {int:  RxEchoVars} = {}
        self.beacons: {int: {str: [Beacon]}} = {}
        self.ax25_stations_settings: {str: DefaultStation} = config_station.get_all_stat_cfg()
        self.ax25_port_settings: {int: DefaultPort} = {}
        self.ax25_ports: {int: AX25Port} = {}
        #######################################################
        # Init Ports/Devices with Config and running as Thread
        for port_id in range(self.max_ports):  # Max Ports
            self.init_port(port_id=port_id)

    def __del__(self):
        self.close_all_ports()
        logger.info("Ende PoPT Ver.: {}".format(VER))

    ######################
    # Connection Handling
    def get_port_by_index(self, index: int):
        return self.ax25_ports[index]

    def close_all(self):
        for k in list(self.all_connections.keys()):
            del self.all_connections[k]
        if self.gui is not None:
            self.gui.ch_btn_status_update()
        self.gui = None
        self.set_gui(None)
        self.close_all_ports()

    def close_all_ports(self):
        """
        if hasattr(self, 'mh_list'):
            self.mh_list.save_mh_data()
            del self.mh_list
        """
        logger.info('Info: Versuche alle Ports zu schließen.')
        if self.is_running:
            self.is_running = False

            for k in list(self.ax25_ports.keys()):
                self.close_port(k)
                # self.ax25_ports[k].loop_is_running = False
                # self.ax25_ports[k].join()

    def close_port(self, port_id: int):
        logger.info('Info: Versuche Port {} zu schließen.'.format(port_id))
        port = self.ax25_ports[port_id]
        port.connections = {}
        port.close()
        c = 0
        while not port.ende:
            time.sleep(0.5)
            # self.sysmsg_to_gui("Hinweis: Warte auf Port " + str(port_id))
            print("Warte auf Port " + str(port_id))
            logger.debug("Warte auf Port " + str(port_id))
            port.close()
            c += 1
            if c == 10:
                break

        # port.join()
        if port_id in self.ax25_ports.keys():
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

    def reinit_port(self, port_id: int):
        if port_id in self.ax25_ports.keys():
            self.close_port(port_id=port_id)
            time.sleep(1)  # Cooldown for Device
            self.init_port(port_id=port_id)

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
            cfg = config_station.PortConfigInit(loaded_stat=self.ax25_stations_settings, port_id=port_id)
            if cfg.parm_PortTyp:
                #########################
                # Init Port/Device
                temp: AX25Port = self.ax25types[cfg.parm_PortTyp](cfg, self)
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
                temp.start()
                ##########################
                # Start Port/Device Thread
                ######################################
                # Gather all Ports in dict: ax25_ports
                if self.gui is not None:
                    temp.set_gui(self.gui)
                self.ax25_ports[port_id] = temp
                self.ax25_port_settings[port_id] = temp.port_cfg
                self.rx_echo[port_id] = RxEchoVars(port_id)
                self.sysmsg_to_gui('Info: Port {} erfolgreich initialisiert.'.format(cfg.parm_PortNr))
                logger.info("Port {} Typ: {} erfolgreich initialisiert.".format(port_id, temp.port_typ))

    def save_all_port_cfgs(self):
        for port_id in self.ax25_ports.keys():
            self.ax25_ports[port_id].port_cfg.save_to_pickl()

    ######################
    # GUI Handling
    def set_gui(self, gui):
        """ PreInit: Set GUI Var """
        if self.gui is None:
            self.gui = gui
            for k in self.ax25_ports.keys():
                # self.ax25_ports[k][1].glb_gui = gui
                self.ax25_ports[k].set_gui(gui)

    def sysmsg_to_gui(self, msg: str = ''):
        if self.gui is not None and self.is_running:
            self.gui.msg_to_monitor(msg)

    ######################
    # Connection Handling
    def insert_conn2all_conn_var(self, new_conn, ind: int = 1):
        if not new_conn.is_link or not new_conn.my_digi_call:
            keys = list(self.all_connections.keys())
            # print("INSERT PRT HANDLER {}".format(keys))

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
                self.gui.ch_btn_status_update()

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

    def del_conn2all_conn_var(self, conn):
        temp = []
        for k in list(self.all_connections.keys()):
            # temp_conn: AX25Conn = self.all_connections[k]
            temp_conn = self.all_connections[k]
            if temp_conn == conn:
                temp.append(k)
        for k in temp:
            # conn: AX25Conn = self.all_connections[k]
            conn = self.all_connections[k]
            conn.ch_index = 0
            if self.gui is not None:
                self.gui.disco_snd()
            del self.all_connections[k]
        if self.gui is not None:
            self.gui.ch_btn_status_update()

    ######################
    # RX-ECHO Handling
    def rx_echo_input(self, ax_frame: AX25Frame, port_id):
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

            # self.rx_echo[k].buff_input(ax_frame=ax_frame, port_id=k)

