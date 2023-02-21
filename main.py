from copy import deepcopy

from gui.guiMainNew import *
from ax25.ax25InitPorts import *

VER = '2.31a'
if __name__ == '__main__':
    #################
    # Init AX25 Stuff
    # !!! Dummy Var for Init AX25PortHandler > AX25PortHandler.parm_port_handler = self
    # ax25port_handler = AX25PortHandler
    ax25port_handler = AX25PortHandler()
    #############
    # INIT GUI
    # if setting_gui:
    try:
        main_win = TkMainWin(ax25port_handler)
    except KeyboardInterrupt:
        pass

    ################
    # On Close Window
    # del main_win
    ax25port_handler.close_all_ports()
    """
    tmp_cfg = []
    for k in ax25port_handler.ax25_ports.keys():
        tmp_cfg.append(ax25port_handler.ax25_ports[k][1])
    del ax25port_handler
    for cfg in tmp_cfg:
        if cfg.parm_PortNr != -1:
            cfg.glb_mh = None
            cfg.glb_gui = None
            cfg.glb_port_handler = None
            file = cfg_data_path + 'port{}'.format(cfg.parm_PortNr)
            f = open(file, 'wb')
            
            dump = cfg
            # print(dump)
            pickle.dump(dump, f, 2)
            f.close()
    """
    print("Ende")
    # MYHEARD.save_mh_data()
