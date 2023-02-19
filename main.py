from gui.guiMainNew import *
from ax25.ax25InitPorts import *

VER = '2.22a'
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
    del ax25port_handler
    print("Ende")
    # MYHEARD.save_mh_data()
