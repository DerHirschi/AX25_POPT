import time

from ax25.ax25Port import *
from config_station import *


class AX25PortHandler(object):
    def __init__(self, glb_MH):
        self.is_running = True
        self.ax25types = {
            'KISSTCP': KissTCP,
            'KISSSER': KISSSerial,
            'AXIP': AXIP,
        }
        ###########################
        # VArs for gathering Stuff
        # self.all_connections: {int: AX25Conn} = {}
        self.all_connections = {}
        self.ax25_ports: {int: AX25Port} = {}
        self.mh = glb_MH
        # self.client_db = cli.ClientDB.ClientDB()
        self.gui = None
        #######################################################
        # Init Ports/Devices with Config and running as Thread
        self.ax25_stations = get_all_stat_cfg()
        for port_id in range(20):   # Max Ports
            self.init_port(port_id=port_id)
            """
            ##########
            # Init CFG
            cfg = PortConfigInit(loaded_stat=self.ax25_stations, port_id=port_id)
            if cfg.parm_PortTyp:
                #########################
                # Init Port/Device
                try:
                    temp = self.ax25types[cfg.parm_PortTyp](cfg, self)
                except AX25DeviceFAIL as e:
                    logger.error('Could not initialise Port {}'.format(cfg.parm_PortNr))
                    logger.error('{}'.format(e))
                else:
                    temp: AX25Port
                    ##########################
                    # Start Port/Device Thread
                    temp.start()
                    ######################################
                    # Gather all Ports in dict: ax25_ports
                    self.ax25_ports[port_id] = temp
            """

    def __del__(self):
        self.close_all_ports()

    def get_port_by_index(self, index: int):
        return self.ax25_ports[index]

    def close_all_ports(self):
        """
        if hasattr(self, 'mh_list'):
            self.mh_list.save_mh_data()
            del self.mh_list
        """
        if self.is_running:
            for k in self.ax25_ports.keys():
                self.ax25_ports[k].loop_is_running = False
                self.ax25_ports[k].join()
        self.is_running = False

    def reinit_all_ports(self):
        for port_id in list(self.ax25_ports.keys()):
            self.reinit_port(port_id)

    def reinit_port(self, port_id: int):
        if port_id in self.ax25_ports.keys():
            port = self.ax25_ports[port_id]
            port.close()
            port.join()
            del self.ax25_ports[port_id]
            del port
            time.sleep(1)   # Cooldown for Device
            self.init_port(port_id=port_id)

    def init_port(self, port_id: int):
        if port_id in self.ax25_ports.keys():
            logger.error('Could not initialise Port {}. Port already in use'.format(port_id))
        else:
            ##########
            # Init CFG
            cfg = PortConfigInit(loaded_stat=self.ax25_stations, port_id=port_id)
            if cfg.parm_PortTyp:
                #########################
                # Init Port/Device
                try:
                    temp = self.ax25types[cfg.parm_PortTyp](cfg, self)
                except AX25DeviceFAIL as e:
                    logger.error('Could not initialise Port {}'.format(cfg.parm_PortNr))
                    logger.error('{}'.format(e))
                else:
                    temp: AX25Port
                    ##########################
                    # Start Port/Device Thread
                    temp.start()
                    ######################################
                    # Gather all Ports in dict: ax25_ports
                    if self.gui is not None:
                        temp.set_gui(self.gui)
                    self.ax25_ports[port_id] = temp

    def set_gui(self, gui):
        """ PreInit: Set GUI Var """
        if self.gui is None:
            self.gui = gui
            for k in self.ax25_ports.keys():
                # self.ax25_ports[k][1].glb_gui = gui
                self.ax25_ports[k].set_gui(gui)

    # def insert_conn2all_conn_var(self, new_conn: AX25Conn, ind: int = 1):
    def insert_conn2all_conn_var(self, new_conn, ind: int = 1):
        if not new_conn.is_link or not new_conn.my_digi_call:
            keys = list(self.all_connections.keys())
            # print("INSERT PRT HANDLER {}".format(keys))

            if keys:
                tr = False
                # Check if Connection is already in all_conn...
                for k in self.all_connections.keys():
                    if new_conn == self.all_connections[k]:
                        tr = True
                        if new_conn.ch_index != k:
                            logger.warning("Channel Index != Real Index !!!")
                            new_conn.ch_index = k
                if not tr:
                    while True:
                        if ind in keys:
                            ind += 1
                        else:
                            new_conn.ch_index = ind
                            self.all_connections[ind] = new_conn
                            break
            else:
                new_conn.ch_index = ind
                self.all_connections[ind] = new_conn
            if new_conn.is_gui:
                new_conn.gui.ch_btn_status_update()

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

    # def del_conn2all_conn_var(self, conn: AX25Conn):
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
        if conn.is_gui:
            conn.gui.ch_btn_status_update()
