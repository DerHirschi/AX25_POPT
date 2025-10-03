from cfg.cfg_fnc import init_dir_struct
from cfg.constant import VER, DEBUG_LOG, POPT_BANNER
from cfg.logger_config import logger, LOG_BOOK
from fnc.os_fnc import is_windows

for el in POPT_BANNER.split('\r')[1:-2]:
    logger.info(el)
if is_windows():
    logger.info(f"Version: {VER} (Windows) wird gestartet.")
else:
    logger.info(f"Version: {VER} (Linux) wird gestartet.")

logger.info(f"DEBUG_LOG: {DEBUG_LOG}")
first_setup  = init_dir_struct()  # Setting up Directory's
if first_setup:
    from setup_wizard.wguiSetup_app import SetupWizardAPP
    SetupWizardAPP()

#############################################
logger.info("Starte Port-Handler")
from ax25.ax25InitPorts import PORT_HANDLER

if __name__ == '__main__':
    logger.info(f"PoPT_{VER} erfolgreich gestartet....")
    LOG_BOOK.info(f"PoPT_{VER} erfolgreich gestartet....")
    #############
    # INIT GUI
    # TODO: if setting_gui (running without GUI option):
    # inp = input('Weiter ?')
    logger.info("Lade GUI")
    import gui.guiMain
    logger.info(f"Starte GUI.")
    gui.guiMain.PoPT_GUI_Main(PORT_HANDLER)

    # PORT_HANDLER.unblock_all_ports()
    # PORT_HANDLER.close_popt()
    logger.info(f"PoPT_{VER} beendet.")
    LOG_BOOK.info(f"PoPT_{VER} beendet.")
