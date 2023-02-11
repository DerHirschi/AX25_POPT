from ax25.ax25Port import *
from config_station import *


class AX25PortInit(object):
    def __init__(self):
        ax25types = {
            'KISSTCP': KissTCP
        }
        self.ax25_ports: {int: AX25Port} = {}
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

                temp = (ax25types[port_cfg.parm_PortTyp](port_cfg), port_cfg)
                #temp[0].start()
                #########################
                print("TEMP {}".format(temp))
                self.ax25_ports[c] = temp
                print("TEMP {}".format(temp))
            c += 1

    def __del__(self):
        for k in  self.ax25_ports.keys():
            self.ax25_ports[k][0].loop_is_running = False
            ax25dev = self.ax25_ports[k][0]
            del ax25dev
