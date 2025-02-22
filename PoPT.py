from cfg.cfg_fnc import init_dir_struct
from cfg.constant import VER, DEBUG_LOG, POPT_BANNER
from cfg.logger_config import logger, LOG_BOOK

for el in POPT_BANNER.split('\r')[1:-2]:
    logger.info(el)
logger.info(f"Version: {VER} wird gestartet.")
logger.info(f"DEBUG_LOG: {DEBUG_LOG}")
init_dir_struct()  # Setting up Directory's
#############################################
import gui.guiMain

if __name__ == '__main__':
    logger.info(f"PoPT_{VER} erfolgreich gestartet....")
    LOG_BOOK.info(f"PoPT_{VER} erfolgreich gestartet....")
    #############
    # INIT GUI
    # TODO: if setting_gui (running without GUI option):
    logger.info(f"Loading GUI.")
    gui.guiMain.PoPT_GUI_Main()

    logger.info(f"PoPT_{VER} beendet.")
    LOG_BOOK.info(f"PoPT_{VER} beendet.")
