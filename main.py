from gui.guiMaín_old import *
from ax25.ax25InitPorts import AX25PortInit
# from ax25.ax25PortHandler import MYHEARD

VER = '0.1a'

if __name__ == '__main__':
    ax25ports_init = AX25PortInit()
    ax25ports = ax25ports_init.ax25_ports
    print(ax25ports)
    try:
        main = TkMainWin(ax25ports)
    except KeyboardInterrupt:
        pass
    del main
    del ax25ports_init
    print("Ende")
    # MYHEARD.save_mh_data()
