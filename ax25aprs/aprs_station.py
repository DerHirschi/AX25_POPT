import time

import aprslib
import logging
from datetime import datetime
from fnc.cfg_fnc import cleanup_obj, save_to_file, load_fm_file, set_obj_att

logger = logging.getLogger(__name__)


class APRS_Station(object):
    def __init__(self):
        self.aprs_parm_call = ''
        self.aprs_parm_loc = ''
        self.aprs_port_id = 0
        # self.aprs_parm_lat: float = 0
        # self.aprs_parm_lon: float = 0

        self.aprs_parm_digi = False
        self.aprs_parm_igate = False
        self.aprs_parm_igate_tx = False
        self.aprs_parm_igate_rx = False
        # self.aprs_beacon_text = ''
        self.aprs_ais = None




class APRS_ais(object):
    def __init__(self):
        print("APRS-IS INIT")
        logger.info("APRS-IS INIT")
        """ APRS-Server Stuff """
        self.ais_call = ''
        self.ais_pass = ''
        self.ais_loc = ''
        self.ais_lat: float = 0
        self.ais_lon: float = 0
        self.add_new_user = False
        # self.ais_host = "cbaprs.dyndns.org", 27234
        self.ais_aprs_stations: {int: APRS_Station} = {}
        self.ais_host = '', 0
        self.ais = None
        self.ais_active = False
        self.ais_rx_buff = []
        """ Global APRS Stuff """
        """
        self.ais_msg_pool = {
            "message": {
                -1: [],      # -1 = AIS > Aprs I-Gate Server
            },
            "bulletin": {
                -1: [],     # -1 = AIS > Aprs I-Gate Server
            },
        }
        """
        """ Loop Control """
        self.loop_is_running = False
        """ Load CFGs and Init (Login to APRS-Server) """
        self.load_conf_fm_file()
        if self.ais_active:
            self.login()

    def save_conf_to_file(self):
        save_date = cleanup_obj(self)
        save_date.ais = None
        save_date.ais_rx_buff = []
        save_date.loop_is_running = False
        save_date.ais_aprs_stations = {}
        for k in self.ais_aprs_stations.keys():
            save_date.ais_aprs_stations[k] = cleanup_obj(self.ais_aprs_stations[k])

        save_to_file('ais.popt', data=save_date)

    def load_conf_fm_file(self):
        load_data = load_fm_file('ais.popt')
        if load_data:
            load_data = cleanup_obj(load_data)
            for att in dir(load_data):
                if '__' not in att:
                    if hasattr(self, att):
                        if not callable(getattr(self, att)):
                            if att not in ['ais', 'ais_rx_buff']:
                                setattr(self, att, getattr(load_data, att))
                            elif att == 'ais_aprs_stations':
                                tmp = {}
                                for k in getattr(load_data, att):
                                    tmp[k] = set_obj_att(APRS_Station(), load_data.ais_aprs_stations[k])
                                    tmp[k].aprs_parm_loc = self.ais_loc
                                load_data.ais_aprs_stations = tmp

    def login(self):
        if not self.ais_active:
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
        print("APRS-IS Login successful")
        logger.info("APRS-IS Login successful")
        return True

    def task(self):
        while self.loop_is_running:
            self.aprs_ais_task()
            time.sleep(0.1)
        print("APRS-AIS Loop END")
        logger.info("APRS-AIS Loop END")

    def aprs_ais_task(self):
        if self.ais is not None:
            if self.ais_active:
                self.ais.consumer(self.callback,
                                  blocking=False,
                                  immortal=True,
                                  raw=False)

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

