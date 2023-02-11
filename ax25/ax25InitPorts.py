import ax25.ax25Port
from ax25.ax25Port import *
from config_station import *


class AX25PortHandler(object):
    def __init__(self):
        ax25types = {
            'KISSTCP': KissTCP
        }
        self.ax25_ports: {int: AX25Port} = {}
        self.mh_list = ax25.ax25Statistics.MH()

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
                #########################
                # Set GLOBALS
                port_cfg.glb_mh = self.mh_list
                port_cfg.glb_port_handler = self
                #########################
                # Init Port/Device
                temp = (ax25types[port_cfg.parm_PortTyp](port_cfg), port_cfg)
                temp[0]: ax25.ax25Port.AX25Port
                ##########################
                # Start Port/Device Thread
                temp[0].start()
                ######################################
                # Gather all Ports in dict: ax25_ports
                self.ax25_ports[c] = temp
            c += 1

    def __del__(self):
        self.close_all_ports()

    def close_all_ports(self):
        for k in self.ax25_ports.keys():
            self.ax25_ports[k][0].loop_is_running = False
            ax25dev = self.ax25_ports[k][0]
            del ax25dev
        if hasattr(self, 'mh_list'):
            self.mh_list.save_mh_data()
            del self.mh_list

    def set_gui(self, gui):
        for k in self.ax25_ports.keys():
            self.ax25_ports[k][1].glb_gui = gui
