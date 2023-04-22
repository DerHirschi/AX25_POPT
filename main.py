import gui.guiMain
import ax25.ax25InitPorts
import logging
from config_station import VER

LANGUAGE = 0    # QUICK FIX
"""
0 = German
1 = English
2 = Dutch
"""

if "dev" in VER:
    log_level = logging.DEBUG
else:
    log_level = logging.WARNING

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename='error.log',
    level=log_level
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    #################
    # Init AX25 Stuff
    GLB_AX25port_handler = ax25.ax25InitPorts.AX25PortHandler()
    #############
    # INIT GUI
    # TODO: if setting_gui (running without GUI option):
    main_win = gui.guiMain.TkMainWin(GLB_AX25port_handler)
    if GLB_AX25port_handler.is_running:
        GLB_AX25port_handler.close_all()

    print("Ende")
