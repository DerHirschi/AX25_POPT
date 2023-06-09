import time

import aprslib
import logging
from datetime import datetime

from ax25aprs.aprs_dec import parse_aprs_fm_ax25frame, parse_aprs_fm_aprsframe
from constant import APRS_SW_ID
from fnc.cfg_fnc import cleanup_obj, save_to_file, load_fm_file, set_obj_att
from fnc.str_fnc import convert_umlaute_to_ascii

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
        self.ack_counter = 0
        self.spooler_buffer = {}
        self.parm_max_n = 2
        self.parm_resend = 60
        """ Loop Control """
        self.loop_is_running = False
        self.non_prio_task_timer = 0
        self.parm_non_prio_task_timer = 1
        self.port_handler = None
        """ Load CFGs and Init (Login to APRS-Server) """
        if load_cfg:
            self.load_conf_fm_file()
        if self.ais_active:
            self.login()

    def save_conf_to_file(self):
        print("Save APRS Conf")
        logger.info("Save APRS Conf")
        save_data = cleanup_obj(set_obj_att(APRS_ais(load_cfg=False), self))
        save_data.ais = None
        save_data.port_handler = None
        save_data.ais_rx_buff = []
        save_data.loop_is_running = False
        save_data.ais_aprs_stations = {}
        save_data.spooler_buffer = {}
        """
        save_date.ais_aprs_msg_pool = {
            "message": [],
            "bulletin": [],
        }
        """
        for k in self.ais_aprs_stations.keys():
            tmp = cleanup_obj(self.ais_aprs_stations[k])
            # tmp.aprs_ais = None
            save_data.ais_aprs_stations[k] = tmp
        save_to_file('ais.popt', data=save_data)

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
            self.prio_tasks()
            self.non_prio_tasks()
            time.sleep(0.1)
        print("APRS-AIS Loop END")
        logger.info("APRS-AIS Loop END")

    def prio_tasks(self):
        self.ais_rx_task()

    def non_prio_tasks(self):
        if time.time() > self.non_prio_task_timer:
            self.non_prio_task_timer = time.time() + self.parm_non_prio_task_timer
            self.spooler_task()
            if self.port_handler is not None:
                if self.port_handler.gui is not None:
                    if self.port_handler.gui.aprs_pn_msg_win is not None:
                        self.port_handler.gui.aprs_pn_msg_win.update_spooler_tree()

    def task_halt(self):
        self.loop_is_running = False

    def ais_rx_task(self):
        if self.ais is not None:
            if self.ais_active:
                self.ais.consumer(self.callback,
                                  blocking=False,
                                  immortal=True,    # TODO reconnect handling
                                  raw=False)

    def ais_tx(self, ais_pack):
        if self.ais is not None:
            if ais_pack:
                try:
                    self.ais.sendall(ais_pack)
                except aprslib.ConnectionError:
                    self.loop_is_running = False
                    del self.ais
                    self.ais = None

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
        self.aprs_msg_sys_rx(port_id='I-NET', aprs_pack=packet)
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
                            if aprs_pack.get('msgNo', False):
                                self.send_ack(formated_pack)
                            self.reset_address_in_spooler(aprs_pack)
                    elif 'bulletin' == aprs_pack['format']:
                        if formated_pack not in self.ais_aprs_msg_pool['bulletin']:
                            self.ais_aprs_msg_pool['bulletin'].append(formated_pack)
                            self.aprs_msg_sys_new_bn(formated_pack)
                            print(f"aprs Bulletin-MSG fm {aprs_pack['from']} {port_id} - {aprs_pack.get('message_text', '')}")

                elif 'response' in aprs_pack:
                    aprs_pack['popt_port_id'] = port_id
                    self.handle_response(pack=aprs_pack)

    def handle_response(self, pack):
        if pack.get('msgNo', False):
            self.handle_ack(pack)

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

    def send_aprs_answer_msg(self, answer_pack, msg='', with_ack=False):
        if answer_pack and msg:
            from_call = answer_pack[1][1].get('addresse', '')
            if from_call in self.port_handler.ax25_stations_settings:
                to_call = answer_pack[1][1].get('from', '')
                path = answer_pack[1][1].get('path', [])
                path.reverse()
                port_id = answer_pack[0]
                # out_pack = dict(answer_pack[1][1])
                aprs_str = f"{from_call}>{APRS_SW_ID}"
                for el in path:
                    if el[-1] == '*':
                        el = el[:-1]
                    aprs_str += f",{el}"
                aprs_str += f"::{to_call.ljust(9)}:dummy"
                out_pack = parse_aprs_fm_aprsframe(aprs_str)
                if out_pack:
                    out_pack['from'] = from_call
                    out_pack['path'] = path
                    out_pack['addresse'] = to_call
                    out_pack['popt_port_id'] = port_id
                    return self.send_pn_msg(out_pack, msg, with_ack)
            return False

    def send_pn_msg(self, pack, msg, with_ack=False):
        msg = convert_umlaute_to_ascii(msg)
        msg_list = []
        while len(msg) > 67:
            msg_list.append(msg[:67])
            msg = msg[67:]
        msg_list.append(msg)
        for el in msg_list:
            if with_ack:
                pack['message_text'] = f":{pack['addresse'].ljust(9)}:{el}" + "{" + f"{int(self.ack_counter)}"
                self.add_to_spooler(pack)
            else:
                pack['message_text'] = f":{pack['addresse'].ljust(9)}:{el}"
                self.send_it(pack)
        return True

    def send_it(self, pack):
        if pack['popt_port_id'] == 'I-NET':
            self.send_as_AIS(pack)
        else:
            self.send_as_UI(pack)

    def add_to_spooler(self, pack):
        # print(f"Spooler in > {pack}")
        pack['N'] = 0
        pack['send_timer'] = 0
        pack['msgNo'] = str(self.ack_counter)
        pack['address_str'] = f"{pack['from']}:{pack['addresse']}"
        self.spooler_buffer[str(self.ack_counter)] = dict(pack)
        self.ack_counter = (self.ack_counter + 1) % 99999

    def del_fm_spooler(self, pack):
        print("del_fm_spooler")
        msg_no = pack.get('msgNo', '')
        ack_pack = self.spooler_buffer.get(msg_no, {})
        if ack_pack.get('address_str', '') == f"{pack.get('addresse', '')}:{pack.get('from', '')}":
            print(f"ACK DEL {msg_no}")
            del self.spooler_buffer[msg_no]
            self.reset_address_in_spooler(pack)

    def reset_address_in_spooler(self, pack):
        add_str = f"{pack.get('addresse', '')}:{pack.get('from', '')}"
        for msg_no in self.spooler_buffer:
            if self.spooler_buffer[msg_no]['address_str'] == add_str:
                self.spooler_buffer[msg_no]['N'] = 0
                self.spooler_buffer[msg_no]['send_timer'] = 0

    def handle_ack(self, pack):
        self.del_fm_spooler(pack)
        self.reset_address_in_spooler(pack)

    def spooler_task(self):
        send = []
        for msg_no in list(self.spooler_buffer.keys()):
            pack = self.spooler_buffer[msg_no]
            if pack['address_str'] not in send:
                send.append(pack['address_str'])
                if pack['send_timer'] < time.time():
                    if pack['N'] < self.parm_max_n:
                        pack['send_timer'] = time.time() + self.parm_resend
                        pack['N'] += 1
                        self.send_it(pack)
                        if pack['N'] == self.parm_max_n:
                            self.del_address_fm_spooler(pack)
                    # else: self.del_fm_spooler(pack, rx=False)

    def del_address_fm_spooler(self, pack):
        for msg_no in list(self.spooler_buffer.keys()):
            if self.spooler_buffer[msg_no]['address_str'] == pack['address_str']:
                self.spooler_buffer[msg_no]['N'] = self.parm_max_n
                # self.del_fm_spooler(pack, rx=False)

    def send_as_UI(self, pack):
        port_id = pack.get('popt_port_id', False)
        ax_port = self.port_handler.ax25_ports.get(port_id, False)
        if ax_port:
            path = pack.get('path', [])
            msg_text = pack.get('message_text', '').encode('ASCII', 'ignore')
            from_call = pack.get('from', '')
            add_str = f"{APRS_SW_ID}"
            for elm in path:
                elm = elm.replace('*', '')
                add_str += f" {elm}"
            ax_port.send_UI_frame(
                own_call=from_call,
                add_str=add_str,
                text=msg_text,
                cmd_poll=(False, True)
            )

    def send_as_AIS(self, pack):
        print(f"send_as_AIS : {pack}")
        msg = pack['message_text']
        pack_str = f"{pack['from']}>{pack['to']},TCPIP*:{msg}"
        print(f" AIS OUT > {pack_str}")
        self.ais_tx(pack_str)

    def send_ack(self, pack_to_resp):

        msg_no = pack_to_resp[1][1].get('msgNo', False)
        print(f"SEND ACK > {msg_no}")
        print(f"SEND ACK > {pack_to_resp[1][1]}")
        if msg_no:
            self.send_aprs_answer_msg(pack_to_resp, f"ack{msg_no}", False)

    def send_rej(self, pack_to_resp):
        pass

