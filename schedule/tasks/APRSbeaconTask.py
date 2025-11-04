from cfg.constant import APRS_POS_BEACON_COMMENT_MAX, APRS_SW_ID, CLI_TYP_SYSOP
from cfg.popt_config import POPT_CFG
from cli.StringVARS import replace_StringVARS
from cfg.logger_config import logger
from fnc.loc_fnc import decimal_degrees_to_aprs


class APRSbeaconTask:
    def __init__(self, porthandler, beacon_conf: dict):
        """
        :param beacon_conf:

        task_typ            = 'APRS-BEACON',
        be_scheduler_cfg    = dict(getNew_schedule_config()),
        be_text             = '',
        be_symbol           = '',
        be_from             = 'NOCALL',
        be_via              = '',
        be_wide             = 0,
        be_ports            = [],
        be_enabled          = True,
        """
        self._conf = beacon_conf
        self._port_handler = porthandler
        self._text = ''

    def _send_APRS_beacon(self):
        """
        ui_conf = {
            'max_conn': 0,
            'port_id': 0,
            'own_call': 'MDBLA1',
            'dest_call': 'MDBLA2',
            'via_calls': ['MDBLA5', 'MDBLA8'],
            'text': b'TEST',
            'cmd_poll': (False, False),
            'pid': 0xF0
        }
        """
        self._text = self._conf.get('be_text', '')
        self._text = replace_StringVARS(self._text,
                                        port_handler=self._port_handler,
                                        )
        self._text = self._text.replace('\n', '\r')[:APRS_POS_BEACON_COMMENT_MAX]
        self._conf['be_text'] = str(self._text)
        self._text = self._build_aprs_beacon(self._conf)
        if not self._text:
            return
        via_str  = self._conf.get('be_via', '')
        wide     = self._conf.get('be_wide', 0)
        via_list = via_str.split(' ')
        while '' in via_list:
            via_list.remove('')
        if wide:
            via_list.append(f"WIDE{wide}-{wide}")
        for port in self._conf.get('be_ports', []):
            ais = self._port_handler.get_aprs_ais()
            aprs_pack = {
                'port_id': port,
                'from': self._conf.get('be_from', 'NOCALL'),
                'to': APRS_SW_ID,
                'path': via_list,
                'raw_message_text': self._text,
            }
            if hasattr(ais, 'send_it'):
                ais.send_it(aprs_pack)


    def send_it(self):
        self._send_APRS_beacon()

    @staticmethod
    def _build_aprs_beacon(aprs_beacon_cfg: dict):
        ais_cfg = POPT_CFG.get_CFG_aprs_ais()
        """ 
        aprs_beacon_cfg = dict(
            be_from='NOCALL',
            be_via='',
            be_wide=0,
            be_symbol      = ("\\", '-'),
            be_text    = ''
        )
        """
        from_call        = aprs_beacon_cfg.get('be_from', 'NOCALL')
        stat_cfg         = POPT_CFG.get_stat_CFG_fm_call(from_call)
        if stat_cfg.get('stat_parm_cli', '') == CLI_TYP_SYSOP:
            msg_typ = '='
        else:
            msg_typ = '!'

        msg_text         = aprs_beacon_cfg.get('be_text', '')
        lat              = ais_cfg.get('ais_lat', 0.0)
        lon              = ais_cfg.get('ais_lon', 0.0)
        if not aprs_beacon_cfg.get('be_symbol', '\\0'):
            return ''
        symbol1, symbol2 = aprs_beacon_cfg.get('be_symbol', '\\0')
        try:
            coordinate = decimal_degrees_to_aprs(lat, lon)
        except Exception as ex:
            logger.error(ex)
            return ''
        return f'{msg_typ}{coordinate[0]}{symbol1}{coordinate[1]}{symbol2}{msg_text[:APRS_POS_BEACON_COMMENT_MAX]}'

