import copy

from cfg.default_config import getNew_BBS_cfg, getNew_maniGUI_parm, \
    getNew_APRS_ais_cfg, getNew_MH_cfg, getNew_digi_cfg, getNew_station_cfg, getNew_port_cfg, getNew_mcast_cfg, \
    getNew_mcast_channel_cfg, getNew_1wire_cfg, getNew_gpio_cfg, getNew_fwdStatistic_cfg
from cfg.constant import CFG_MAIN_data_file, MAX_PORTS, DEF_TEXTSIZE
from cfg.cfg_fnc import load_fm_pickle_file, save_to_pickle_file, get_all_stat_CFGs, del_user_data, \
    save_station_CFG_to_file, load_all_port_cfg_fm_file, save_all_port_cfg_to_file
from cfg.logger_config import logger


class Main_CFG:
    def __init__(self):
        logger.info('Main CFG: Init')
        self._config = {}
        # TODO RX-Echo CFG
        self._default_cfg_tab = {
            ##########################
            # -- BBS
            'bbs_main': getNew_BBS_cfg,
            'bbs_fwd_statistics': {},
            # 'pms_home_bbs': getNew_BBS_FWD_cfg,
            ##########################
            # -- MH
            'mh_cfg': getNew_MH_cfg,
            ##########################
            # -- APRS
            'aprs_node_tab': {},
            'aprs_ais': getNew_APRS_ais_cfg,
            ##########################
            # -- GUI
            # GUI Main
            'gui_main_parm': getNew_maniGUI_parm,
            'gui_channel_vars': {},
            'gui_pacman': {},
            ##########################
            # -- Beacon
            'beacon_tasks': [],
            ##########################
            # -- Dual Port
            'dualPort_cfg': {},
            ##########################
            # -- DIGI
            'digi_cfg': {},
            ##########################
            # -- PIPE CFGs
            # 'pipe_cfg': self._load_PIPE_CFG_fm_file,
            'pipe_cfgs': {},
            ##########################
            # -- STATION CFGs
            'stat_cfgs': {},
            ##########################
            # -- PORT CFGs
            'port_cfgs': {},
            'block_list': {},
            ##########################
            # -- MCast CFG
            'mcast_cfg': getNew_mcast_cfg,
            ##########################
            # -- 1Wire CFG
            '1wire_cfg': getNew_1wire_cfg,
            ##########################
            # -- GPIO CFG
            'gpio_cfg': getNew_gpio_cfg,
        }
        """ Main CFGs """
        self._load_CFG_fm_file()        # Other Configs
        self._set_all_default_CFGs()
        self._clean_old_CFGs()
        self._update_old_CFGs()
        """"""
        # self._load_PIPE_CFG_fm_file()
        """ Station CFGs """
        self._load_STAT_CFG_fm_file()   # Station Configs
        self._update_old_STAT_CFGs()
        """ Port CFGs """
        self._load_PORT_CFG_fm_file()   # Port Configs
        self._update_old_PORT_CFGs()
        """ MCast CFGs"""
        self._update_old_MCast_ch_cfgs()
        """ BBS CFGs"""
        self._update_BBS_cfg()
        """
        print('---------- PIPE CFG -------------')
        for call, cfg in self._config['pipe_cfgs'].items():
            print(f'>> {call}')
            print(f'{cfg}')
            print('------------------------')
        """

        logger.info(f'--------Loaded CFGs --------')
        for conf_k, conf in self._config.items():
            logger.info(f'Main CFG: load {conf_k} - Size: {len(conf)} - str_size: {len(str(conf))}')
        logger.info(f'-------- Loaded CFGs ENDE --------')
        logger.info('Main CFG: Init complete')
        ### DEV ################################################
        # self._config['1wire_cfg'] = getNew_1wire_cfg()
        # print(getNew_BBS_cfg())


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

    def _update_old_CFGs(self):
        # TODO Clean Configs aprs-cfg etc.
        for cfg_key, cfg in self._config.items():
            if cfg_key not in ['gui_channel_vars']:
                new_cfg = self.get_default_CFG_by_key(cfg_key)
                if new_cfg:
                    for k in new_cfg.keys():
                        new_cfg[k] = cfg.get(k, new_cfg[k])
                    self._config[cfg_key] = new_cfg

    ####################
    # File Fnc
    def _load_CFG_fm_file(self):
        logger.info(f'Main CFG: Load from {CFG_MAIN_data_file}')
        # print(f'Main CFG: Load from {self._config_filename}')
        config: dict = load_fm_pickle_file(CFG_MAIN_data_file)
        if config:
            self._config = dict(config)
        else:
            logger.warning("Main CFG: MainConfig wasn't found. Generating new Default Configs !! ")
            self._set_all_default_CFGs()
        """
        logger.debug('-----------------------------')
        for cfg_name, cfg in self._config.get('bbs_main', {}).items():
            logger.debug(f"bbs_main:{cfg_name}> {cfg}")
        # self._config.read(self._config_filename)
        logger.debug('-----------------------------')
        """

    def save_MAIN_CFG_to_file(self):
        logger.info(f'Main CFG: Config Saved to {CFG_MAIN_data_file}')
        """
        if DEBUG_LOG:
            logger.debug(self._config['stat_cfgs'])
            logger.debug(self._config['port_cfgs'])
            logger.debug(self._config['pipe_cfgs'])
            logger.debug(f'-------- Stat CFG --------')
            for conf_k, conf in self._config.get('stat_cfgs', {}).items():
                logger.debug(f'Station CFG: {conf_k}')
                logger.debug(f'- {conf}')
        """

        tmp_stat_cfgs = dict(self._config['stat_cfgs'])
        tmp_port_cfgs = dict(self._config['port_cfgs'])
        self._config['stat_cfgs'] = {}  # Don't save Stat CFG in MainCFG
        self._config['port_cfgs'] = {}  # Don't save Port CFG in MainCFG

        logger.info(f'-------- MAIN CFG Save --------')
        for conf_k, conf in self._config.items():
            logger.info(f'Main CFG: save {conf_k} - Size: {len(conf)}')
            # logger.debug(f'- type: {type(conf)} - size: {len(conf)} - str_size: {len(str(conf))}')

        save_to_pickle_file(CFG_MAIN_data_file, dict(self._config))

        self._config['stat_cfgs'] = tmp_stat_cfgs
        self._config['port_cfgs'] = tmp_port_cfgs
        logger.info(f'-------- MAIN CFG Save ENDE --------')

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
        # print('---------- Stat CFG--------------')
        # print(self._config['stat_cfgs'])
        logger.info(f'-------- Stat CFG --------')
        for conf_k, conf in self._config.get('stat_cfgs', {}).items():
            logger.info(f'Station CFG: load {conf_k}')
            # logger.debug(f'- {conf}')
        # return get_all_pipe_cfg()   # Get CFGs fm Station CFG

    def _update_old_STAT_CFGs(self):
        new_stat_cfgs = {}
        for call, conf in self._config.get('stat_cfgs', {}).items():
            new_conf = getNew_station_cfg()
            new_keys = list(new_conf.keys())
            for k in new_keys:
                new_conf[k] = conf.get(k, new_conf.get(k, None))
            new_stat_cfgs[call] = new_conf
        self._config['stat_cfgs'] = new_stat_cfgs

        # print('---------- Stat CFG Cleanup --------------')
        # print(self._config['stat_cfgs'])
        logger.info(f'-------- Stat CFG Cleanup --------')
        for conf_k, conf in self._config.get('stat_cfgs', {}).items():
            logger.info(f'Station CFG: Cleanup {conf_k}')
            # logger.debug(f'- {conf}')


    ###########################################
    # PORTs
    def _load_PORT_CFG_fm_file(self):
        self._config['port_cfgs'] = load_all_port_cfg_fm_file()
        logger.info(f'-------- Port CFG Load --------')
        for conf_k, conf in self._config.get('port_cfgs', {}).items():
            logger.info(f'Port CFG: load {conf_k}')
            # logger.debug(f'- {conf}')

    def _update_old_PORT_CFGs(self):
        new_port_cfgs = {}
        for port_id, conf in self._config.get('port_cfgs', {}).items():
            new_conf = getNew_port_cfg()
            new_keys = list(new_conf.keys())
            for k in new_keys:
                new_conf[k] = conf.get(k, new_conf.get(k, None))
            new_port_cfgs[port_id] = new_conf
        self._config['port_cfgs'] = new_port_cfgs

        logger.info(f'-------- Port CFG Cleanup --------')
        for conf_k, conf in self._config.get('port_cfgs', {}).items():
            logger.info(f'Port CFG: Cleanup {conf_k}')
            # logger.debug(f'- {conf}')

    def save_PORT_CFG_to_file(self):
        save_all_port_cfg_to_file(self._config.get('port_cfgs', {}))
        logger.info(f'-------- Port CFG Save --------')
        for conf_k, conf in self._config.get('port_cfgs', {}).items():
            logger.info(f'Port CFG: save {conf_k}')
            # logger.debug(f'- {conf}')


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
    def get_CFG_MH(self):
        return self._config['mh_cfg']

    def set_CFG_MH(self, data: dict):
        self._config['mh_cfg'] = data

    ####################
    # APRS
    def get_CFG_aprs_ais(self):
        return self._config['aprs_ais']

    def set_CFG_aprs_ais(self, data: dict):
        self._config['aprs_ais'] = data

    def get_APRS_node_tab(self):
        return self._config['aprs_node_tab']

    def set_APRS_node_tab(self, node_tab: dict):
        self._config['aprs_node_tab'] = node_tab

    ########################################################
    # GUI
    def get_guiCFG_language(self):
        return int(self._config['gui_main_parm'].get('gui_lang', 0))

    def get_guiCFG_text_size(self):
        return int(self._config['gui_main_parm'].get('gui_parm_text_size', DEF_TEXTSIZE))

    def get_guiCFG_textWin_pos(self):
        return tuple(self._config['gui_main_parm'].get('gui_cfg_txtWin_pos', (0, 1, 2)))

    def get_guiCFG_STYLE_NAME(self):
        return int(self._config['gui_main_parm'].get('gui_lang', ('black', '#d9d9d9')))

    def get_guiCFG_locator(self):
        return str(self._config['gui_main_parm'].get('gui_cfg_locator', ''))

    def get_guiCFG_qth(self):
        return str(self._config['gui_main_parm'].get('gui_cfg_qth', ''))

    # GUI PARM
    def load_guiPARM_main(self):
        return dict(self._config['gui_main_parm'])

    def save_guiPARM_main(self, data: dict):
        self._config['gui_main_parm'] = dict(data)

    def set_guiPARM_main(self, data: dict):
        if not data:
            return False
        conf_data = dict(self._config.get('gui_main_parm', getNew_maniGUI_parm()))
        for conf_k in list(data.keys()):
            if conf_k in list(conf_data.keys()):
                # if type(data[conf_k]) is type(conf_k[conf_k]):
                conf_data[conf_k] = data[conf_k]
        self._config['gui_main_parm'] = conf_data

    def get_guiPARM_main_param_by_key(self, conf_key: str):
        return self._config.get('gui_main_parm', {}).get(conf_key, None)

    # Channel Vars
    def load_guiCH_VARS(self):
        return dict(self._config.get('gui_channel_vars', {}))

    def save_guiCH_VARS(self, data: dict):
        self._config['gui_channel_vars'] = dict(data)

    # F-Text
    def get_f_text_fm_id(self, f_id: int):
        return tuple(
            self._config.get('gui_main_parm', {})
            .get('gui_f_text_tab' , {})
            .get(f_id, (b'', 'UTF-8'))
        )

    def set_f_text_f_id(self, f_id: int, text_and_enc: tuple):
        if 1 > f_id > 12:
            return False
        if len(text_and_enc) != 2:
            return False
        ftext_dict = dict(self._config.get('gui_main_parm', {}).get('gui_f_text_tab' , {}))
        ftext_dict[f_id] = text_and_enc
        self._config['gui_main_parm']['gui_f_text_tab'] = ftext_dict
        return True

    # Pacman
    def get_pacman_data(self):
        return dict(self._config.get('gui_pacman', {}))

    def set_pacman_data(self, data: dict):
        if not data:
            return
        self._config['gui_pacman'] = dict(data)

    def get_pacman_fix(self):
        return bool(self._config['gui_main_parm'].get('gui_cfg_pacman_fix', False))
    """
    def set_pacman_fix(self, value: bool):
        self._config['gui_main_parm']['gui_cfg_pacman_fix'] = bool(value)
    """

    #################################################
    # Beacon
    def get_Beacon_tasks(self):
        return list(self._config.get('beacon_tasks', []))

    def set_Beacon_tasks(self, data: list):
        self._config['beacon_tasks'] = list(data)

    #################################################
    # Dual Port
    def get_dualPort_CFG(self):
        return dict(self._config.get('dualPort_cfg', {}))

    def set_dualPort_CFG(self, cfg: dict):
        self._config['dualPort_cfg'] = dict(cfg)

    #################################################
    # DIGI
    def get_digi_CFG(self):
        return dict(self._config.get('digi_cfg', {}))

    def get_digi_CFG_for_Call(self, call: str):
        return dict(self._config.get('digi_cfg', {}).get(call, self.get_digi_default_CFG()))

    def get_digi_is_enabled(self, call: str):
        if not call:
            return False
        return bool(self._config.get('digi_cfg', {}).get(call, self.get_digi_default_CFG()).get('digi_enabled', False))

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
        return dict(self._config.get('pipe_cfgs', {}))

    def get_pipe_CFG_fm_UID(self, call, port_id=-1):
        cfg_keys = list(self._config.get('pipe_cfgs', {}).keys())
        lookup_k = f'{port_id}-{call}'
        if lookup_k in cfg_keys:
            return dict(self._config.get('pipe_cfgs', {}).get(lookup_k, {}))
        return {}

    def del_pipe_CFG_fm_CallPort(self, call, port_id=-1):
        cfg_keys = list(self._config.get('pipe_cfgs', {}).keys())
        lookup_k = f'{port_id}-{call}'
        if lookup_k in cfg_keys:
            del self._config['pipe_cfgs'][lookup_k]
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
            del self._config['pipe_cfgs'][uid]

    def del_pipe_CFG_fm_call(self, call: str):
        if not call:
            return False
        for k in list(self.get_pipe_CFG().keys()):
            i = len(k) - len(call)
            if call == k[i:]:
                del self._config['pipe_cfgs'][k]

    ###########################################
    # Station
    def get_stat_CFGs_by_typ(self, typ='USER'):
        stat_cfg = dict(self._config.get('stat_cfgs', {}))
        ret = {}
        for call, stat_cfg in stat_cfg.items():
            if stat_cfg.get('stat_parm_cli', 'NO-CLI') == typ:
                ret[str(call)] = dict(stat_cfg)
        return ret

    def get_stat_CFGs(self):
        return dict(self._config.get('stat_cfgs', {}))

    def get_stat_CFG_fm_call(self, call):
        if not call:
            return {}
        return dict(self._config.get('stat_cfgs', {}).get(call, {}))

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
        return True

    ###########################################
    # Port
    def get_port_CFGs(self):
        return dict(self._config.get('port_cfgs', {}))

    def get_port_CFG_fm_id(self, port_id: int):
        if 0 > port_id > MAX_PORTS - 1:
            return {}
        return dict(self._config.get('port_cfgs', {}).get(port_id, {}))

    def get_stationCalls_fm_port(self, port_id: int):
        port_cfg = self.get_port_CFG_fm_id(port_id)
        if not port_cfg:
            return []
        return list(port_cfg.get('parm_StationCalls', []))

    def get_all_stationCalls(self):
        port_cfgs = self.get_port_CFGs()
        if not port_cfgs:
            return []
        ret = []
        for port_id, port_cfg in port_cfgs.items():
            ret += list(port_cfg.get('parm_StationCalls', []))
        return ret

    def set_port_CFG_fm_id(self, port_id: int, port_cfg: dict):
        if 0 > port_id > MAX_PORTS - 1:
            return False
        if not port_cfg:
            return False
        if not port_cfg.get('parm_PortTyp', ''):
            return False
        self._config['port_cfgs'][port_id] = dict(port_cfg)
        return True

    def del_port_CFG_fm_id(self, port_id: int):
        if 0 > port_id > MAX_PORTS - 1:
            return False
        if port_id not in self._config.get('port_cfgs', {}):
            return False
        del self._config['port_cfgs'][port_id]
        return True

    ###########################################
    # MCAST
    def _update_old_MCast_ch_cfgs(self):
        logger.info('Main CFG: Update MCast Channel Configs')
        new_ch_cfgs = {}
        old_ch_cfgs = self._config.get('mcast_cfg', {}).get('mcast_ch_conf', {})
        for ch_id, old_cfg in old_ch_cfgs.items():
            new_cfg = getNew_mcast_channel_cfg(channel_id=ch_id)
            for cfg_name, cfg_val in new_cfg.items():
                new_cfg[cfg_name] = old_cfg.get(cfg_name, cfg_val)
            new_ch_cfgs[ch_id] = new_cfg
        if not self._config.get('mcast_cfg', {}):
            logger.error(f"Main CFG: Error _update_old_MCAST_ch_cfgs()")
            self._config['mcast_cfg'] = getNew_mcast_cfg()
        self._config['mcast_cfg']['mcast_ch_conf'] = new_ch_cfgs

    def get_MCast_CFG(self):
        return dict(self._config.get('mcast_cfg', getNew_mcast_cfg()))
        # return getNew_mcast_cfg()

    def get_MCast_CH_CFGs(self):
        return dict(self._config.get('mcast_cfg', {}).get('mcast_ch_conf', {}))

    def get_MCast_server_call(self):
        stat_cfgs = self.get_stat_CFGs()
        for call, stat_cfg in stat_cfgs.items():
            if stat_cfg.get('stat_parm_cli', '') == 'MCAST':
                return str(call)
        return ''

    def set_MCast_CFG(self, mcast_cfg: dict):
        if not mcast_cfg:
            logger.error('Main CFG: set_MCast_CFG no Config')
            return False
        self._config['mcast_cfg'] = dict(mcast_cfg)
        return True

    ###########################################
    # 1Wire
    def get_1wire_sensor_cfg(self):
        return dict(self._config.get('1wire_cfg', {}).get('sensor_cfg', {}))

    def get_1wire_loop_timer(self):
        return int(self._config.get('1wire_cfg', {}).get('loop_timer', 60))

    def set_1wire_sensor_cfg(self, sensor_cfg: dict):
        cfg = dict(self._config.get('1wire_cfg', getNew_1wire_cfg()))
        cfg['sensor_cfg'] = dict(sensor_cfg)
        self._config['1wire_cfg'] = dict(cfg)

    def set_1wire_loop_timer(self, loop_timer: int):
        loop_timer = max(30, loop_timer)
        cfg = dict(self._config.get('1wire_cfg', getNew_1wire_cfg()))
        cfg['loop_timer'] = int(loop_timer)
        self._config['1wire_cfg'] = dict(cfg)

    ###########################################
    # GPIO
    def get_gpio_cfg(self):
        """
        gpio_conf = {}
        for pin in range(10, 15):
            pin_name, pin_cfg = getNew_gpio_pin_cfg(pin)
            test_fnc_cfg: dict = getNew_gpio_fnc_cfg_dxAlarm()
            pin_cfg['function_cfg'] = test_fnc_cfg
            gpio_conf[pin_name] = pin_cfg
        for pin in range(15, 20):
            pin_name, pin_cfg = getNew_gpio_pin_cfg(pin)
            test_fnc_cfg: dict = getNew_gpio_fnc_cfg_ConnAlarm()
            pin_cfg['function_cfg'] = test_fnc_cfg
            gpio_conf[pin_name] = pin_cfg
        return dict(gpio_conf)
        """
        return dict(self._config.get('gpio_cfg', getNew_gpio_cfg()))

    def set_gpio_cfg(self, gpio_cfg: dict):
        self._config['gpio_cfg'] = dict(gpio_cfg)

    ###########################################
    # BBS
    def _update_BBS_cfg(self):
        if 'pms_main' in  self._config:
            self._config['bbs_main'] = dict(self._config['pms_main'])
            del self._config['pms_main']

        if 'home_bbs_cfg' in self._config['bbs_main']:
            self._config['bbs_main']['fwd_bbs_cfg'] = dict(self._config['bbs_main']['home_bbs_cfg'])
            del self._config['bbs_main']['home_bbs_cfg']

    def get_BBS_cfg(self):
        return copy.deepcopy(self._config.get('bbs_main', getNew_BBS_cfg()))

    def get_BBS_FWD_cfg(self, bbs_call: str):
        return copy.deepcopy(self._config
                             .get('bbs_main', getNew_BBS_cfg())
                             .get('fwd_bbs_cfg', {})
                             .get(bbs_call, {})
        )

    def set_BBS_cfg(self, bbs_cfg: dict):
        self._config['bbs_main'] = dict(bbs_cfg)

    def get_BBS_AutoMail_cfg(self):
        return copy.deepcopy(self._config.get('bbs_main', getNew_BBS_cfg()).get('auto_mail_tasks', []))

    def get_fwd_statistics(self, bbs_call: str):
        return self._config.get('bbs_fwd_statistics', {}).get(bbs_call, getNew_fwdStatistic_cfg())

    def set_fwd_statistics(self, bbs_call: str, stat_dict: dict):
        try:
            self._config['bbs_fwd_statistics'][bbs_call] = copy.deepcopy(stat_dict)
        except Exception as ex:
            logger.error(ex)

    ###########################################
    # Block List
    def get_block_list(self):
        return self._config.get('block_list', {})

    def get_block_list_by_id(self, port_id: int):
        return self._config.get('block_list', {}).get(port_id, {})

    def set_block_list(self, block_tab: dict):
        self._config['block_list'] = block_tab


POPT_CFG = Main_CFG()
