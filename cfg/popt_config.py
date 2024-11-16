from cfg.default_config import getNew_PMS_cfg, getNew_homeBBS_cfg, getNew_maniGUI_parm, \
    getNew_APRS_ais_cfg, getNew_MH_cfg, getNew_digi_cfg
from cfg.constant import CFG_MAIN_data_file, LANGUAGE
from cfg.cfg_fnc import load_fm_file, save_to_file, get_all_stat_CFGs, del_user_data, \
    save_station_CFG_to_file  # , get_all_pipe_cfg
from cfg.logger_config import logger


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
            # 'aprs_station': getNew_APRS_Station_cfg,
            'aprs_station': {},
            'aprs_ais': getNew_APRS_ais_cfg,
            # -- GUI
            # GUI Main
            'gui_main_parm': getNew_maniGUI_parm,
            'gui_channel_vars': getNew_dict,
            # -- Beacon
            'beacon_tasks': [],
            'dualPort_cfg': {},
            # -- DIGI
            'digi_cfg': {},  # TODO
            # -- PIPE CFGs
            # 'pipe_cfg': self._load_PIPE_CFG_fm_file,
            'pipe_cfgs': {},
            # -- PIPE CFGs
            'stat_cfgs': {},
        }
        self._load_CFG_fm_file()
        # self._load_PIPE_CFG_fm_file()   # TODO cleanup wenn Station CFG implementiert ist
        self._load_STAT_CFG_fm_file()
        self._set_all_default_CFGs()
        self._clean_old_CFGs()
        """
        print('---------- PIPE CFG -------------')
        for call, cfg in self._config['pipe_cfgs'].items():
            print(f'>> {call}')
            print(f'{cfg}')
            print('------------------------')
        """

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
    def _load_CFG_fm_file(self):
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

    """
    # PIPE
    @staticmethod
    def _load_PIPE_CFG_fm_file():
        # self._config['pipe_cfgs'] = get_all_pipe_cfg()
        # print('-------------------------------')
        # print(get_all_pipe_cfg())
        # print(self._config['pipe_cfgs'])
        return get_all_pipe_cfg()   # Get CFGs fm Station CFG
    """

    # STATIONs
    def _load_STAT_CFG_fm_file(self):
        self._config['stat_cfgs'] = get_all_stat_CFGs()
        print('----------Stat CFG--------------')
        print(self._config['stat_cfgs'])
        logger.info(f'-------- Stat CFG --------')
        for conf_k, conf in self._config.get('stat_cfgs', {}).items():
            logger.info(f'Station CFG: load {conf_k}')
            logger.debug(f'- {conf}')
        logger.info(f'-------- MAIN CFG --------')
        for conf_k, conf in self._config.items():
            logger.info(f'Main CFG: load {conf_k} - Size: {len(conf)}')
            logger.debug(f'- type: {type(conf)} - size: {len(conf)} - str_size: {len(str(conf))}')
        logger.info(f'-------- Stat CFG ENDE --------')
        # return get_all_pipe_cfg()   # Get CFGs fm Station CFG

    def save_CFG_to_file(self):
        logger.info(f'Main CFG: Config Saved to {self._config_filename}')
        print(f'Main CFG: Config Saved to {self._config_filename}')
        print('----------Stat CFG--------------')
        print(self._config['stat_cfgs'])
        tmp_stat_cfgs = dict(self._config['stat_cfgs'])
        logger.debug(f'-------- Stat CFG --------')
        for conf_k, conf in self._config.get('stat_cfgs', {}).items():
            logger.debug(f'Station CFG: {conf_k}')
            logger.debug(f'- {conf}')
        self._config['stat_cfgs'] = {}  # TODO just for DEBUGGING
        logger.info(f'-------- MAIN CFG Save --------')
        for conf_k, conf in self._config.items():
            logger.info(f'Main CFG: save {conf_k} - Size: {len(conf)}')
            logger.debug(f'- type: {type(conf)} - size: {len(conf)} - str_size: {len(str(conf))}')
        save_to_file(self._config_filename, dict(self._config))
        self._config['stat_cfgs'] = tmp_stat_cfgs
        logger.info(f'-------- MAIN CFG Save ENDE --------')


    ####################
    # Global CFG by Key
    def get_default_CFG_by_key(self, cfg_key: str):
        def_cfg = self._default_cfg_tab.get(cfg_key, None)
        if def_cfg is not None:
            if callable(def_cfg):
                return def_cfg()
            return def_cfg

    def get_CFG_by_key(self, cfg_key: str):
        if cfg_key not in self._config.keys():
            self._config[cfg_key] = dict(self.get_default_CFG_by_key(cfg_key))
        return self._config[cfg_key]

    def set_CFG_by_key(self, cfg_key: str, data):
        self._config[cfg_key] = data

    ####################
    # MH
    def load_CFG_MH(self):
        return self._config['mh_cfg']

    def save_CFG_MH(self, data: dict):
        self._config['mh_cfg'] = data

    ####################
    # APRS
    def get_CFG_aprs_station(self):
        return self._config['aprs_station']

    def get_CFG_aprs_ais(self):
        return self._config['aprs_ais']

    def set_CFG_aprs_ais(self, data: dict):
        self._config['aprs_ais'] = data

    ####################
    # GUI
    def get_guiCFG_language(self):
        # return self._config['gui_main_parm'].get('gui_lang', 0)
        return LANGUAGE

    # GUI PARM
    def load_guiPARM_main(self):
        return self._config['gui_main_parm']

    def save_guiPARM_main(self, data: dict):
        self._config['gui_main_parm'] = data

    def set_guiPARM_main(self, data: dict):
        if not data:
            return False
        conf_data = self._config.get('gui_main_parm', getNew_maniGUI_parm())
        for conf_k in list(data.keys()):
            if conf_k in list(conf_data.keys()):
                # if type(data[conf_k]) is type(conf_k[conf_k]):
                conf_data[conf_k] = data[conf_k]
        self._config['gui_main_parm'] = conf_data

    def get_guiPARM_main(self, conf_key: str):
        return self._config.get('gui_main_parm', {}).get(conf_key, None)

    # Channel Vars
    def load_guiCH_VARS(self):
        return self._config['gui_channel_vars']

    def save_guiCH_VARS(self, data: dict):
        self._config['gui_channel_vars'] = data

    #################################################
    # Beacon
    def get_Beacon_tasks(self):
        return self._config.get('beacon_tasks', [])

    def set_Beacon_tasks(self, data: list):
        self._config['beacon_tasks'] = list(data)

    #################################################
    # Dual Port
    def get_dualPort_CFG(self):
        return self._config.get('dualPort_cfg', {})

    def set_dualPort_CFG(self, cfg: dict):
        self._config['dualPort_cfg'] = dict(cfg)

    #################################################
    # DIGI
    def get_digi_CFG(self):
        return self._config.get('digi_cfg', {})

    def get_digi_CFG_for_Call(self, call: str):
        return self._config.get('digi_cfg', {}).get(call, self.get_digi_default_CFG())

    def get_digi_is_enabled(self, call: str):
        if not call:
            return False
        return self._config.get('digi_cfg', {}).get(call, self.get_digi_default_CFG()).get('digi_enabled', False)

    @staticmethod
    def get_digi_default_CFG():
        return getNew_digi_cfg()

    def set_digi_CFG(self, cfg: dict):
        self._config['digi_cfg'] = dict(cfg)
        return True

    def set_digi_CFG_f_call(self, call: str, cfg: dict):
        if not call:
            return False
        if call == 'NOCALL':
            return False
        self._config['digi_cfg'][call] = dict(cfg)
        return True

    def del_digi_CFG_fm_call(self, call: str):
        if not call:
            return False
        if call not in self._config.get('digi_cfg', {}):
            return False
        del self._config['digi_cfg'][call]

    ###########################################
    # PIPE
    def get_pipe_CFG(self):
        return self._config.get('pipe_cfgs', {})

    def get_pipe_CFG_fm_UID(self, call, port_id=-1):
        cfg_keys = list(self._config.get('pipe_cfgs', {}).keys())
        lookup_k = f'{port_id}-{call}'
        if lookup_k in cfg_keys:
            return self._config.get('pipe_cfgs', {}).get(lookup_k, {})
        return {}

    def del_pipe_CFG_fm_CallPort(self, call, port_id=-1):
        cfg_keys = list(self._config.get('pipe_cfgs', {}).keys())
        lookup_k = f'{port_id}-{call}'
        if lookup_k in cfg_keys:
            del self._config['pipe_cfgs'][lookup_k]
            print(self._config['pipe_cfgs'])
            return True
        return False

    def set_pipe_CFG(self, pipe_cfg):
        call = pipe_cfg.get('pipe_parm_own_call', '')
        port = pipe_cfg.get('pipe_parm_port', -1)
        if not call:
            return
        uid = f'{port}-{call}'
        self._config['pipe_cfgs'][uid] = pipe_cfg

    def del_pipe_CFG(self, uid):
        # UID = f'{port}-{call}'
        if uid in self._config.get('pipe_cfgs', {}):
            print(f"Del Pipe-CFG: {uid}")
            del self._config['pipe_cfgs'][uid]

    def del_pipe_CFG_fm_call(self, call: str):
        if not call:
            return False
        for k in list(self.get_pipe_CFG().keys()):
            i = len(k) - len(call)
            if call == k[i:]:
                print(f"Del Pipe-CFG: {k}")
                del self._config['pipe_cfgs'][k]

    ###########################################
    # Station
    def get_stat_CFGs(self):
        return self._config.get('stat_cfgs', {})

    def get_stat_CFG_fm_call(self, call):
        if not call:
            return {}
        return self._config.get('stat_cfgs', {}).get(call, {})

    def get_stat_CFG_keys(self):
        return list(self._config.get('stat_cfgs', {}))

    def set_stat_CFG_fm_conf(self, conf: dict):
        if not conf:
            return False
        stat_call = conf.get('stat_parm_Call', '')
        if not stat_call:
            return False
        self._config['stat_cfgs'][stat_call] = dict(conf)
        save_station_CFG_to_file(dict(conf))
        return True

    def del_stat_CFG_fm_call(self, call):
        if not call:
            return False
        if call not in self._config.get('stat_cfgs', {}):
            return False
        del self._config['stat_cfgs'][call]
        self.del_pipe_CFG_fm_call(call=call)
        self.del_digi_CFG_fm_call(call=call)
        del_user_data(call=call)

POPT_CFG = Main_CFG()
