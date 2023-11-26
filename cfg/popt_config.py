import logging

from cfg.default_config import getNew_PMS_cfg, getNew_homeBBS_cfg
from constant import CFG_MAIN_data_file
from fnc.cfg_fnc import load_fm_file, save_to_file

logger = logging.getLogger(__name__)


class Main_CFG:
    def __init__(self):
        logger.info('Main CFG: Init')
        print('Main CFG: Init')
        self._config_filename = CFG_MAIN_data_file
        self._config = {}
        self._default_cfg_tab = {
            'pms_main': getNew_PMS_cfg,
            'pms_home_bbs': getNew_homeBBS_cfg,
        }
        self.load_CFG_fm_file()

    def __del__(self):
        pass

    def _set_all_default_CFGs(self):
        for cfg_key in self._default_cfg_tab.keys():
            if cfg_key not in self._config:
                self._config[cfg_key] = self.get_default_CFG_by_key(cfg_key)

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
        save_to_file(self._config_filename, dict(self._config))
        """
        with open(self._config_filename, 'w') as configfile:
            self._config.write(configfile)
        """
    def get_default_CFG_by_key(self, cfg_key: str):
        def_cfg = self._default_cfg_tab.get(cfg_key, None)
        if def_cfg:
            return def_cfg()

    def get_CFG_by_key(self, cfg_key: str):
        if cfg_key not in self._config.keys():
            self._config[cfg_key] = dict(self.get_default_CFG_by_key(cfg_key))
        return self._config[cfg_key]

    def set_CFG_by_key(self, cfg_key: str, data):
        self._config[cfg_key] = data


POPT_CFG = Main_CFG()
