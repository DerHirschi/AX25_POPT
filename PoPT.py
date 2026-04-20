from core.popt_core import PoPTCore

from cfg.cfg_fnc import init_dir_struct
from cfg.constant import VER, DEBUG_LOG, POPT_BANNER
from cfg.logger_config import logger, LOG_BOOK
from cfg.popt_config import POPT_CFG
from fnc.os_fnc import is_windows, is_macos

GUI = True
#############################################
if __name__ == '__main__':
    # ========================================
    # Logging
    for el in POPT_BANNER.split('\r')[1:-2]:
        logger.info(el)
    if is_macos():
        logger.info(f"Version: {VER} (MacOS) wird gestartet.")
    elif is_windows():
        logger.info(f"Version: {VER} (Windows) wird gestartet.")
    else:
        logger.info(f"Version: {VER} (Linux) wird gestartet.")

    logger.info(f"DEBUG_LOG: {DEBUG_LOG}")

    # ========================================
    # Checking/Init Directory's
    first_setup = init_dir_struct()  # Setting up Directory's
    if GUI:
        if first_setup or not POPT_CFG.get_first_setup():
            # ========================================
            # SetupWizard
            from setup_wizard.wguiSetup_app import SetupWizardAPP
            SetupWizardAPP()

    # ========================================
    # Popt Core
    logger.info("Starte Popt-Core")
    popt_core = PoPTCore(gui_app=GUI)
    logger.info(f"PoPT_{VER} erfolgreich gestartet....")
    LOG_BOOK.info(f"PoPT_{VER} erfolgreich gestartet....")

    # ========================================
    # Popt GUI
    logger.info("Lade GUI")
    from gui.guiMain.guiMain import PoPT_GUI_Main
    logger.info(f"Starte GUI.")
    PoPT_GUI_Main(popt_core)

    # ========================================
    # Popt Ende
    logger.info(f"PoPT_{VER} beendet.")
    LOG_BOOK.info(f"PoPT_{VER} beendet.")
