import time

import aprslib
import logging
from datetime import datetime
from fnc.cfg_fnc import cleanup_obj, save_to_file, load_fm_file

logger = logging.getLogger(__name__)


class APRS_Station(object):
    def __init__(self):
        self.aprs_parm_call = ''
        self.aprs_parm_loc = ''
        self.aprs_parm_lat = ''
        self.aprs_parm_lon = ''

        self.aprs_parm_digi = False
        self.aprs_parm_igate = False
        self.aprs_parm_igate_tx = False
        self.aprs_parm_igate_rx = False

        # self.aprs_beacon_text = ''
        self.ais = None


class APRS_ais(object):
    def __init__(self):
        print("APRS-AIS INIT")
        logger.info("APRS-AIS INIT")
        self.ais_call = ''
        self.ais_pass = ''
        self.ais_loc = ''
        self.add_new_user = False
        # self.ais_host = "cbaprs.dyndns.org", 27234
        self.ais_host = '', 0
        self.ais = None
        self.active = False
        self.loop_is_running = False
        self.ais_rx_buff = []
        self.load_conf_fm_file()
        if self.active:
            self.login()

    def save_conf_to_file(self):
        save_date = cleanup_obj(self)
        save_date.ais = None
        save_to_file('ais.popt', data=save_date)

    def load_conf_fm_file(self):
        load_data = load_fm_file('ais.popt')
        if load_data:
            load_data = cleanup_obj(load_data)
            for att in dir(load_data):
                if '__' not in att:
                    if not callable(getattr(self, att)):
                        if att not in ['ais', 'ais_rx_buff']:
                            setattr(self, att, getattr(load_data, att))

    def login(self):
        if not self.active:
            return False
        if not self.ais_call:
            return False
        if self.ais_host == ('', 0):
            return False
        if not self.ais_host[0] or not self.ais_host[1]:
            return False

        self.ais = aprslib.IS(callsign=self.ais_call,
                              passwd=self.ais_pass,
                              host=self.ais_host[0],
                              port=self.ais_host[1],
                              skip_login=False)
        try:
            self.ais.connect()
        except aprslib.ConnectionError:
            self.ais = None
            return False
        except aprslib.LoginError:
            self.ais = None
            return False
        except IndexError:
            self.ais = None
            return False
        return True

    def task(self):
        if self.ais is None:
            self.loop_is_running = False
            return False

        while self.loop_is_running and self.active:
            self.ais.consumer(self.callback,
                              blocking=False,
                              immortal=True,
                              raw=False)
            time.sleep(0.1)
        print("APRS-AIS Loop END")
        logger.info("APRS-AIS Loop END")

    def task_halt(self):
        self.loop_is_running = False

    def callback(self, packet):
        self.ais_rx_buff.append(
            (datetime.now().strftime('%H:%M:%S'),
             packet)
        )
        # print(packet)

    def ais_close(self):
        if self.ais is not None:
            self.ais.close()

# APRS_AIS = APRS_ais()
