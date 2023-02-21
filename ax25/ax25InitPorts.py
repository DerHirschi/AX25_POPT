from ax25.ax25Connection import AX25Conn
from ax25.ax25Port import *
from config_station import *


class AX25PortHandler(object):
    def __init__(self):
        self.ax25types = {
            'KISSTCP': KissTCP,
            'KISSSER': KISSSerial,
            'AXIP': AXIP,
        }
        self.ax25_ports: {int: AX25Port} = {}
        # self.mh_list = ax25.ax25Statistics.MH()
        # self.client_db = cli.ClientDB.ClientDB()
        self.gui = None
        #######################################################
        # Init Ports/Devices with Config and running as Thread
        c = 0
        # port_cfg: DefaultPortConfig
        stations = {}
        for port_cfg in [Port0,
                         Port1,
                         Port2,
                         Port3,
                         Port4,
                         Port5,
                         Port6,
                         Port7,
                         Port8,
                         Port9,
                         Port10
                         ]:
            if port_cfg.parm_PortTyp:
                port_cfg.parm_PortNr = c
                ##########
                # Init CFG
                cfg = port_cfg(stations)
                for st in cfg.parm_Stations:
                    if st.stat_parm_Call not in stations.keys():
                        stations[st.stat_parm_Call] = st
                #########################
                # Set GLOBALS
                # cfg.glb_mh = self.mh_list
                cfg.glb_port_handler = self
                #########################
                # Init Port/Device
                try:
                    temp = self.ax25types[cfg.parm_PortTyp](cfg)
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
                    self.ax25_ports[c] = temp
            c += 1
        ###########################
        # VArs for gathering Stuff
        self.all_connections: {int: AX25Conn} = {}

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
        for k in self.ax25_ports.keys():
            # cfg = self.ax25_ports[k][1]
            # cfg.save_to_pickl()
            self.ax25_ports[k].loop_is_running = False
            self.ax25_ports[k].join()

    def set_gui(self, gui):
        """ PreInit: Set GUI Var """
        if self.gui is None:
            self.gui = gui
            for k in self.ax25_ports.keys():
                # self.ax25_ports[k][1].glb_gui = gui
                self.ax25_ports[k].set_gui(gui)

    def insert_conn2all_conn_var(self, new_conn: AX25Conn, ind: int = 1):
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
            conn: AX25Conn = self.all_connections[k]
            if conn.zustand_exec.stat_index in [0]:
                temp.append(k)
        for k in temp:
            conn: AX25Conn = self.all_connections[k]
            conn.ch_index = 0
            del self.all_connections[k]

    def del_conn2all_conn_var(self, conn: AX25Conn):
        temp = []
        for k in list(self.all_connections.keys()):
            temp_conn: AX25Conn = self.all_connections[k]
            if temp_conn == conn:
                temp.append(k)
        for k in temp:
            conn: AX25Conn = self.all_connections[k]
            conn.ch_index = 0
            if self.gui is not None:
                self.gui.disco_snd()
            del self.all_connections[k]
        if conn.is_gui:
            conn.gui.ch_btn_status_update()
