import gui.guiMain
from config_station import logger
from constant import VER

if __name__ == '__main__':
    logger.info(f"PoPT_{VER} start....")
    #############
    # INIT GUI
    # TODO: if setting_gui (running without GUI option):
    logger.info(f"Loading GUI.")
    gui.guiMain.TkMainWin()

    logger.info(f"PoPT_{VER} ENDE.")
    print('ENDE')
