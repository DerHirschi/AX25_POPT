import logging

from cfg.default_config import getNew_PMS_cfg, getNew_homeBBS_cfg, getNew_maniGUI_parm, getNew_APRS_Station_cfg, \
    getNew_APRS_ais_cfg, getNew_MH_cfg
from cfg.constant import CFG_MAIN_data_file
from fnc.cfg_fnc import load_fm_file, save_to_file

logger = logging.getLogger(__name__)


def getNew_dict():
    return {}


class Main_CFG:
    def __init__(self):
        logger.info('Main CFG: Init')
        print('Main CFG: Init')
        self._config_filename = CFG_MAIN_data_file
        self._config = {}
        self._default_cfg_tab = {
            # -- PMS
            'pms_main': getNew_PMS_cfg,
            'pms_home_bbs': getNew_homeBBS_cfg,
            # -- MH
            'mh_cfg': getNew_MH_cfg,
            # -- APRS
            'aprs_station': getNew_APRS_Station_cfg,
            'aprs_ais': getNew_APRS_ais_cfg,
            # -- GUI
            # GUI Main
            'gui_main_parm': getNew_maniGUI_parm,
            'gui_channel_vars': getNew_dict,
        }
        self.load_CFG_fm_file()
        self._set_all_default_CFGs()
        self._clean_old_CFGs()

    ####################
    # Init Stuff
    def _set_all_default_CFGs(self):
        for cfg_key in self._default_cfg_tab.keys():
            if cfg_key not in list(self._config.keys()):
                self._config[cfg_key] = self.get_default_CFG_by_key(cfg_key)

    def _clean_old_CFGs(self):
        for cfg_key in list(self._config.keys()):
            if cfg_key not in self._default_cfg_tab.keys():
                del self._config[cfg_key]
            # TODO Clean Configs itself except gui_channel_vars

    ####################
    # File Fnc
    def load_CFG_fm_file(self):
        logger.info(f'Main CFG: Load from {self._config_filename}')
        print(f'Main CFG: Load from {self._config_filename}')
        config = load_fm_file(self._config_filename)
        if config:
            self._config = dict(config)
        else:
            print("Main CFG: MainConfig wasn't found. Generating new Default Configs !! ")
            logger.warning("Main CFG: MainConfig wasn't found. Generating new Default Configs !! ")
            self._set_all_default_CFGs()

        # self._config.read(self._config_filename)

    def save_CFG_to_file(self):
        logger.info(f'Main CFG: Config Saved to {self._config_filename}')
        print(f'Main CFG: Config Saved to {self._config_filename}')
        # print(f'Main CFG: Config  {self._config}')
        save_to_file(self._config_filename, dict(self._config))

    ####################
    # Global CFG by Key
    def get_default_CFG_by_key(self, cfg_key: str):
        def_cfg = self._default_cfg_tab.get(cfg_key, None)
        if def_cfg is not None:
            return def_cfg()

    def get_CFG_by_key(self, cfg_key: str):
        if cfg_key not in self._config.keys():
            self._config[cfg_key] = dict(self.get_default_CFG_by_key(cfg_key))
        return self._config[cfg_key]

    def set_CFG_by_key(self, cfg_key: str, data):
        self._config[cfg_key] = data

    ####################
    # MH
    def load_CFG_MH(self):
        return dict(self._config['mh_cfg'])

    def save_CFG_MH(self, data: dict):
        self._config['mh_cfg'] = data

    ####################
    # APRS
    def load_CFG_aprs_station(self):
        return dict(self._config['aprs_station'])

    def load_CFG_aprs_ais(self):
        return dict(self._config['aprs_ais'])

    def save_CFG_aprs_ais(self, data: dict):
        self._config['aprs_ais'] = data

    ####################
    # GUI
    def get_guiCFG_language(self):
        return int(self._config['gui_main_parm'].get('gui_lang', 0))

    # GUI PARM
    def load_guiPARM_main(self):
        return dict(self._config['gui_main_parm'])

    def save_guiPARM_main(self, data: dict):
        self._config['gui_main_parm'] = data

    # Channel Vars
    def load_guiCH_VARS(self):
        return dict(self._config['gui_channel_vars'])

    def save_guiCH_VARS(self, data: dict):
        self._config['gui_channel_vars'] = data


POPT_CFG = Main_CFG()
