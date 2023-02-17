import cli.ClientDB
from ax25.ax25Connection import AX25Conn
from ax25.ax25Port import *
from config_station import *



class AX25PortHandler(object):
    def __init__(self):
        ax25types = {
            'KISSTCP': KissTCP,
            'KISSSER': KISSSerial,
            'AXIPCL': AXIPClient,
        }
        self.ax25_ports: {int: (AX25Port, DefaultPortConfig)} = {}
        self.mh_list = ax25.ax25Statistics.MH()
        self.client_db = cli.ClientDB.ClientDB()
        self.gui = None
        #######################################################
        # Init Ports/Devices with Config and running as Thread
        c = 0
        port_cfg: DefaultPortConfig
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
                #########################
                # Set GLOBALS
                port_cfg.glb_mh = self.mh_list
                port_cfg.glb_port_handler = self
                #########################
                # Init Port/Device
                try:
                    temp = (ax25types[port_cfg.parm_PortTyp](port_cfg), port_cfg)
                except AX25DeviceFAIL as e:
                    temp = False
                    logger.error('Could not initialise Port {}'.format(port_cfg.parm_PortNr))
                    logger.error('{}'.format(e))
                if temp:
                    temp[0]: AX25Port
                    ##########################
                    # Start Port/Device Thread
                    temp[0].start()
                    ######################################
                    # Gather all Ports in dict: ax25_ports
                    self.ax25_ports[c] = temp
            c += 1
        ###########################
        # VArs for gathering Stuff
        self.all_connections: {int: AX25Conn} = {}

    def __del__(self):
        self.close_all_ports()

    def close_all_ports(self):
        for k in self.ax25_ports.keys():
            self.ax25_ports[k][0].loop_is_running = False
            ax25dev = self.ax25_ports[k][0]
            # ax25dev.device.close()
            del ax25dev
        if hasattr(self, 'mh_list'):
            self.mh_list.save_mh_data()
            del self.mh_list

    def set_gui(self, gui):
        """ PreInit: Set GUI Var """
        if self.gui is None:
            self.gui = gui
        for k in self.ax25_ports.keys():
            self.ax25_ports[k][1].glb_gui = gui

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
            del self.all_connections[k]
        if conn.is_gui:
            conn.gui.ch_btn_status_update()
