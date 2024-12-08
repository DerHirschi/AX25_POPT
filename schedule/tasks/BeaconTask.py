from cli.StringVARS import replace_StringVARS
from fnc.file_fnc import get_str_fm_file
from cfg.logger_config import logger


class BeaconTask:
    def __init__(self, porthandler, beacon_conf: dict):
        """
        :param beacon_conf:

         'task_typ': 'BEACON',
        'port_id': 0,
        'is_enabled': True,
        'typ': 'Text',      # "Text", "File", "MH"
        'own_call': 'NOCALL',
        'dest_call': 'BEACON',
        'via_calls': [],
        # 'axip_add': ('', 0),
        'text': 'TEST',
        'text_filename': '',
        'cmd_poll': (False, False),
        'pid': 0xF0,
        'scheduler_cfg': dict(getNew_schedule_config()),
        """
        self._conf = beacon_conf
        self._port_handler = porthandler
        self._text = ''

    def _send_UI(self):
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
        if not self._text:
            # print('Beacon: kein Text gesetzt!')
            logger.warning('Beacon: kein Text gesetzt!')
            return
        self._text = replace_StringVARS(self._text,
                                        port=self._port_handler.get_port_by_id(self._conf.get('port_id', 0)),
                                        )
        add_str = self._conf.get('dest_call', '')
        vias = ' '.join(self._conf.get('via_calls', []))
        if vias:
            add_str += ' ' + vias
        ui_frame_cfg = {
            'port_id': self._conf.get('port_id', 0),
            'own_call': self._conf.get('own_call', 'NOCALL'),
            'add_str': add_str,
            'text': self._text.encode('UTF-8', 'ignore')[:256],
            'cmd_poll': self._conf.get('cmd_poll', (False, False)),
            'pid': self._conf.get('pid', 0xF0)
        }
        self._port_handler.send_UI(ui_frame_cfg)

    def send_it(self):
        beacon_fnc = {
            "Text": self._set_text,
            "File": self._set_text_fm_file,
            "MH": self._set_text_fm_mh,
        }.get(self._conf.get('typ', ''), None)
        if callable(beacon_fnc):
            beacon_fnc()
            self._send_UI()

    def _set_text(self):
        self._text = self._conf.get('text', '').replace('\n', '\r')
        # self._text = text.encode('UTF-8', 'ignore')

    def _set_text_fm_file(self):
        file_n = self._conf.get('text_filename', '')
        if not file_n:
            self._text = ''
            return
        text = get_str_fm_file(file_n)
        if text:
            self._text = text.replace('\n', '\r')
            return
        self._text = ''

    def _set_text_fm_mh(self):
        mh = self._port_handler.get_MH()
        if not mh:
            self._text = ''
            return
        self._text = mh.mh_out_beacon(max_ent=12)

