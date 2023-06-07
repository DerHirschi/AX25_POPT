import time

import aprslib
import logging
from datetime import datetime

from ax25aprs.aprs_dec import parse_aprs_fm_ax25frame
from constant import APRS_SW_ID
from fnc.cfg_fnc import cleanup_obj, save_to_file, load_fm_file, set_obj_att

logger = logging.getLogger(__name__)


class APRS_Station(object):
    def __init__(self):
        self.aprs_parm_loc = ''
        self.aprs_port_id = 0
        # self.aprs_parm_lat: float = 0
        # self.aprs_parm_lon: float = 0
        self.aprs_parm_digi = False
        self.aprs_parm_igate = False
        self.aprs_parm_igate_tx = False
        self.aprs_parm_igate_rx = False
        # self.aprs_beacon_text = ''
        # self.aprs_ais = None


class APRS_ais(object):
    def __init__(self, load_cfg=True):
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
        self.ais_aprs_msg_pool = {
            "message": [],
            "bulletin": [],
        }
        """ Loop Control """
        self.loop_is_running = False
        self.port_handler = None
        """ Load CFGs and Init (Login to APRS-Server) """
        if load_cfg:
            self.load_conf_fm_file()
        if self.ais_active:
            self.login()

    def save_conf_to_file(self):
        print("Save APRS Conf")
        logger.info("Save APRS Conf")
        save_data = set_obj_att(APRS_ais(load_cfg=False), self)
        save_date = cleanup_obj(save_data)
        save_date.ais = None
        save_date.port_handler = None
        save_date.ais_rx_buff = []
        save_date.loop_is_running = False
        save_date.ais_aprs_stations = {}
        """
        save_date.ais_aprs_msg_pool = {
            "message": [],
            "bulletin": [],
        }
        """
        for k in self.ais_aprs_stations.keys():
            tmp = cleanup_obj(self.ais_aprs_stations[k])
            # tmp.aprs_ais = None
            save_date.ais_aprs_stations[k] = tmp
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
                                    # tmp[k].aprs_ais = self

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
            self.ais_rx()
            time.sleep(0.1)
        print("APRS-AIS Loop END")
        logger.info("APRS-AIS Loop END")

    def task_halt(self):
        self.loop_is_running = False

    def ais_tx(self, ais_pack):
        if self.ais is not None:
            if ais_pack:
                try:
                    self.ais.sendall(ais_pack)
                except aprslib.ConnectionError:
                    self.loop_is_running = False
                    del self.ais
                    self.ais = None

    def ais_rx(self):
        if self.ais is not None:
            if self.ais_active:
                self.ais.consumer(self.callback,
                                  blocking=False,
                                  immortal=True,
                                  raw=False)

    def ais_close(self):
        if self.ais is not None:
            self.loop_is_running = False
            self.ais.close()
            del self.ais
            self.ais = None
            self.save_conf_to_file()

    def callback(self, packet):
        self.ais_rx_buff.append(
            (datetime.now().strftime('%d/%m/%y %H:%M:%S'),
             packet)
        )
        self.aprs_msg_sys_rx(port_id=-1, aprs_pack=packet)
        # print(packet)

    #########################################
    # APRS MSG System
    def aprs_msg_sys_rx(self, port_id, aprs_pack: {}):
        if "format" in aprs_pack:
            if aprs_pack['format'] in ['message', 'bulletin']:
                formated_pack = (port_id,
                                 (datetime.now().strftime('%d/%m/%y %H:%M:%S'), aprs_pack)
                                 )
                if 'message_text' in aprs_pack:
                    if 'message' == aprs_pack['format']:
                        if formated_pack not in self.ais_aprs_msg_pool['message']:
                            self.ais_aprs_msg_pool['message'].append(formated_pack)
                            self.aprs_msg_sys_new_pn(formated_pack)
                            print(f"aprs PN-MSG fm {aprs_pack['from']} {port_id} - {aprs_pack.get('message_text', '')}")
                    elif 'bulletin' == aprs_pack['format']:
                        if formated_pack not in self.ais_aprs_msg_pool['bulletin']:
                            self.ais_aprs_msg_pool['bulletin'].append(formated_pack)
                            self.aprs_msg_sys_new_bn(formated_pack)
                            print(f"aprs Bulletin-MSG fm {aprs_pack['from']} {port_id} - {aprs_pack.get('message_text', '')}")
                elif 'response' in aprs_pack:
                    pass    # TODO

    """
    def check_duplicate_msg(self, aprs_pack, msg_typ: str):
        check_msg_typ = self.ais_aprs_msg_pool[msg_typ]
        for f_msg in check_msg_typ:
            if aprs_pack == f_msg[1][1]:
                return True
        return False
    """
    def update_pn_msg_gui(self, aprs_pack):
        if self.port_handler is not None:
            if self.port_handler.gui is not None:
                if self.port_handler.gui.aprs_pn_msg_win is not None:
                    self.port_handler.gui.aprs_pn_msg_win.update_tree_single_pack(aprs_pack)

    def aprs_msg_sys_new_pn(self, formated_pack: (int, (str, dict))):
        print(
            f"aprs PN-MSG fm {formated_pack[1][1]['from']} {formated_pack[0]} - {formated_pack[1][1].get('message_text', '')}")
        self.update_pn_msg_gui(formated_pack)

    def aprs_msg_sys_new_bn(self, formated_pack: (int, (str, dict))):
        print(f"aprs Bulletin-MSG fm {formated_pack[1][1]['from']} {formated_pack[0]} - {formated_pack[1][1].get('message_text', '')}")

    def aprs_ax25frame_rx(self, port_id, ax25_frame):
        aprs_pack = parse_aprs_fm_ax25frame(ax25_frame)
        if aprs_pack:
            msg_format = aprs_pack.get("format", '')
            if msg_format:
                if msg_format in ['message', 'bulletin']:
                    self.aprs_msg_sys_rx(port_id=port_id, aprs_pack=aprs_pack)

    def ais_pack_tcpip(self, from_call: str, msg: str):
        # "MD6TES-2>APZPOP,TCPIP*:!5251.12N" + '/' + "01109.78E.27.235MHz TEST"  < Direkt
        # "MD6TES-2>APZPOP:!5251.12N" + '/' + "01109.78E.27.235MHz TEST"         < I-Gate
        print(f"raw: {from_call} - {msg}")
        pack_str = f"{from_call}>{APRS_SW_ID}"
        pack_str += f",TCPIP*:{msg}"
        print(pack_str)
        self.ais_tx(pack_str)
