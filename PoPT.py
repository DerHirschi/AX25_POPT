from cfg.constant import VER, DEBUG_LOG
from cfg.logger_config import logger

logger.info(f"PoPT_{VER} wird gestartet.")
logger.info(f"DEBUG_LOG: {DEBUG_LOG}")
import gui.guiMain



if __name__ == '__main__':
    logger.info(f"PoPT_{VER} erfolgreich gestartet....")
    #############
    # INIT GUI
    # TODO: if setting_gui (running without GUI option):
    logger.info(f"Loading GUI.")
    gui.guiMain.PoPT_GUI_Main()

    logger.info(f"PoPT_{VER} ENDE.")
    print('ENDE')
