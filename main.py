import gui.guiMain
import ax25.ax25InitPorts
import logging
from constant import VER

LANGUAGE = 0    # QUICK FIX
"""
0 = German
1 = English
2 = Dutch
"""

if "dev" in VER:
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename='error.log',
    level=log_level
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info(f"PoPT_{VER} start....")
    #################
    # Init AX25 Stuff
    logger.info(f"Init Ports.")
    GLB_AX25port_handler = ax25.ax25InitPorts.AX25PortHandler()
    logger.info(f"Init Ports done.")
    #############
    # INIT GUI
    # TODO: if setting_gui (running without GUI option):
    logger.info(f"Loading GUI.")
    main_win = gui.guiMain.TkMainWin(GLB_AX25port_handler)
    if GLB_AX25port_handler.is_running:
        logger.info(f"Closing Ports.")
        GLB_AX25port_handler.close_all()
        logger.info(f"Closing Ports done.")

    logger.info(f"PoPT_{VER} ENDE.")
    print('ENDE')
