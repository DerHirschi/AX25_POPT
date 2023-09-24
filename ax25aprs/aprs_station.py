import time
from collections import deque

import aprslib
import logging
from datetime import datetime

from ax25aprs.aprs_dec import parse_aprs_fm_ax25frame, parse_aprs_fm_aprsframe, extract_ack
from constant import APRS_SW_ID, APRS_TRACER_COMMENT
from fnc.cfg_fnc import cleanup_obj, save_to_file, load_fm_file, set_obj_att
from fnc.loc_fnc import decimal_degrees_to_aprs
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
        self.ais_host = 'cbaprs.dyndns.org', 27234
        self.ais = None
        self.ais_mon_gui = None
        self.wx_tree_gui = None
        self.ais_active = False
        self.ais_rx_buff = deque([] * 5000, maxlen=5000)
        # self.ais_new_rx_buff = []
        self._dbl_pack = []
        """ Global APRS Stuff """
        self.aprs_msg_pool = {
            "message": [],
            "bulletin": [],
        }
        self.aprs_wx_msg_pool = {}
        self._ack_counter = 0
        self.spooler_buffer = {}
        self._parm_max_n = 2
        self._parm_resend = 60
        """ Loop Control """
        self.loop_is_running = False
        self._non_prio_task_timer = 0
        self._parm_non_prio_task_timer = 1
        self.port_handler = None
        self._del_spooler_tr = False
        self._wx_update_tr = False
        """ Watchdog """
        self._watchdog_last = time.time()
        self._parm_watchdog = 20  # Sec.
        """ Beacon Tracer """
        self.be_tracer_active = False
        self.be_tracer_interval = 5
        self.be_tracer_port = 0
        self.be_tracer_station = 'NOCALL'
        self.be_tracer_wide = 1
        self.be_tracer_traced_packets = {}

        # self._be_tracer_dest = APRS_SW_ID
        # self._be_tracer_comment = APRS_TRACER_COMMENT
        self._be_tracer_timer = time.time()
        """ Load CFGs and Init (Login to APRS-Server) """
        if load_cfg:
            self._load_conf_fm_file()
        if self.ais_active:
            self.login()

    def del_ais_rx_buff(self):
        self.ais_rx_buff = deque([] * 5000, maxlen=5000)

    def save_conf_to_file(self):
        print("Save APRS Conf")
        logger.info("Save APRS Conf")
        save_data = cleanup_obj(set_obj_att(APRS_ais(load_cfg=False), self))
        save_data.ais = None
        save_data.ais_mon_gui = None
        save_data.wx_tree_gui = None
        save_data.port_handler = None
        save_data.ais_rx_buff = []
        save_data.loop_is_running = False
        save_data.ais_aprs_stations = {}
        # save_data.aprs_wx_msg_pool = {}
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

    def _load_conf_fm_file(self):
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
        self.watchdog_reset()
        if not self.ais_active:
            return False
        if not self.ais_call:
            self.ais_active = False
            return False
        if self.ais_host == ('', 0):
            self.ais_active = False
            return False
        if not self.ais_host[0] or not self.ais_host[1]:
            self.ais_active = False
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
        self.loop_is_running = True
        return True

    def task(self):
        # self.prio_tasks()
        self._non_prio_tasks()

    """
    def prio_tasks(self):
        pass
        # self.ais_rx_task()
    """

    def _non_prio_tasks(self):
        # print("non Prio")
        if time.time() > self._non_prio_task_timer:
            # self.ais_rx_task()
            self._non_prio_task_timer = time.time() + self._parm_non_prio_task_timer
            if self.ais_active:
                self._watchdog_task()
            if self._del_spooler_tr:
                self._flush_spooler_buff()
                self._del_spooler_tr = False
            self._spooler_task()
            if self.port_handler is not None:
                if self.port_handler.gui is not None:
                    if self.port_handler.gui.aprs_pn_msg_win is not None:
                        self.port_handler.gui.aprs_pn_msg_win.update_spooler_tree()

    def aprs_wx_tree_task(self):
        if self.wx_tree_gui is not None:
            if self._wx_update_tr:
                self._wx_update_tr = False
                self.wx_tree_gui.update_tree_data()

    """
    def task_halt(self):
        self.loop_is_running = False
    """

    def ais_rx_task(self):
        if self.ais is not None:
            if self.ais_active:
                print("Consumer")
                while self.loop_is_running:
                    try:
                        self.ais.consumer(self.callback,
                                          blocking=False,
                                          immortal=True,  # TODO reconnect handling
                                          raw=False)
                    except ValueError:
                        # self.ais_active = False
                        del self.ais
                        self.ais = None
                        self.loop_is_running = False
                        print("Consumer ValueError")
                        logger.error("APRS Consumer ValueError")
                        break
                    except aprslib.LoginError:
                        del self.ais
                        self.ais = None
                        self.loop_is_running = False
                        print("Consumer LoginError")
                        logger.warning("APRS Consumer LoginError")
                        break
                    if self.loop_is_running:
                        time.sleep(0.5)
                    else:
                        break
                print("Consumer ENDE")

    def _ais_tx(self, ais_pack):
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
        """ RX fm APRS-Server"""
        self.watchdog_reset()
        self.ais_rx_buff.append(
            (datetime.now().strftime('%d/%m/%y %H:%M:%S'),
             packet)
        )
        if self.ais_mon_gui is not None:
            self.ais_mon_gui.pack_to_mon(
                datetime.now().strftime('%d/%m/%y %H:%M:%S'),
                packet)
        self._aprs_proces_rx(port_id='I-NET', aprs_pack=packet)
        # print(packet)

    def aprs_ax25frame_rx(self, port_id, ax25_frame):
        """ RX fm AX25Frame (HF/AXIP) """
        aprs_pack = parse_aprs_fm_ax25frame(ax25_frame)
        self._aprs_proces_rx(port_id=port_id, aprs_pack=aprs_pack)

    def _aprs_proces_rx(self, port_id, aprs_pack):
        if aprs_pack:
            # APRS PN/BULLETIN MSG
            if aprs_pack.get("format", '') in ['message', 'bulletin', 'thirdparty']:
                self._aprs_msg_sys_rx(port_id=port_id, aprs_pack=aprs_pack)
            # APRS Weather
            elif aprs_pack.get("weather", False):
                new_aprs_pack = self._correct_wrong_wx_data(aprs_pack)
                if new_aprs_pack:
                    self._aprs_wx_msg_rx(port_id=port_id, aprs_pack=new_aprs_pack)
                else:
                    print("APRS Weather Pack correction Failed!")
                    print(f"Org Pack: {aprs_pack}")
                    logger.warning("APRS Weather Pack correction Failed!")
                    logger.warning(f"Org Pack: {aprs_pack}")

    def _aprs_wx_msg_rx(self, port_id, aprs_pack):
        from_aprs = aprs_pack.get('from', '')
        if from_aprs:
            if not self.aprs_wx_msg_pool.get(from_aprs, False):
                self.aprs_wx_msg_pool[from_aprs] = deque([], maxlen=500)
            self.aprs_wx_msg_pool[from_aprs].append(
                (datetime.now().strftime('%d/%m/%y %H:%M:%S'),
                 aprs_pack,
                 port_id)
            )
            if self.wx_tree_gui is not None:
                self._wx_update_tr = True
            # print(aprs_pack)

    @staticmethod
    def _correct_wrong_wx_data(aprs_pack):
        _raw = aprs_pack.get('raw', '')
        if _raw:
            if 'h100b' in _raw:
                _raw = _raw.replace('h100b', 'h00b')
                return parse_aprs_fm_aprsframe(_raw)
        return aprs_pack

    def get_wx_data(self):
        return dict(self.aprs_wx_msg_pool)

    def watchdog_reset(self):
        self._watchdog_last = time.time()

    def _watchdog_task(self):
        if self.ais_active:
            if time.time() > self._watchdog_last + self._parm_watchdog:
                print("APRS-Server Watchdog: Try reconnecting to APRS-Server !")
                logger.warning("APRS-Server Watchdog: Try reconnecting to APRS-Server !")
                if self.port_handler is not None:
                    self.ais_close()
                    if self.login():
                        self.port_handler.init_aprs_ais()
                else:
                    self.ais_close()

    #########################################
    # APRS MSG System
    def _aprs_msg_sys_rx(self, port_id, aprs_pack: {}):
        if aprs_pack.get('format', '') == 'thirdparty':
            # print(f"THP > {aprs_pack['subpacket']}")
            path = aprs_pack.get('path', [])
            aprs_pack = dict(aprs_pack['subpacket'])
            aprs_pack['path'] = path
            aprs_pack['message_text'], ack = extract_ack(aprs_pack.get('message_text', ''))
            if ack is not None:
                aprs_pack['msgNo'] = ack

        if aprs_pack.get('format', '') in ['message', 'bulletin']:
            if not aprs_pack.get('msgNo', False):
                aprs_pack['message_text'], ack = extract_ack(aprs_pack.get('message_text', ''))
                if ack is not None:
                    aprs_pack['msgNo'] = ack
            formated_pack = (port_id,
                             (datetime.now().strftime('%d/%m/%y %H:%M:%S'), aprs_pack)
                             )
            if 'message_text' in aprs_pack:
                if 'message' == aprs_pack['format']:
                    if formated_pack not in self.aprs_msg_pool['message']:
                        if [port_id, aprs_pack['from'], aprs_pack.get('msgNo', ''),
                            aprs_pack.get('message_text', '')] not in self._dbl_pack:
                            self._dbl_pack.append([port_id, aprs_pack['from'], aprs_pack.get('msgNo', ''),
                                                   aprs_pack.get('message_text', '')])
                            self.aprs_msg_pool['message'].append(formated_pack)
                            self._aprs_msg_sys_new_pn(formated_pack)
                            # print(f"aprs PN-MSG fm {aprs_pack['from']} {port_id} - {aprs_pack.get('message_text', '')}")
                    if aprs_pack.get('msgNo', False):
                        self._send_ack(formated_pack)
                    self._reset_address_in_spooler(aprs_pack)
                elif 'bulletin' == aprs_pack['format']:
                    if formated_pack not in self.aprs_msg_pool['bulletin']:
                        self.aprs_msg_pool['bulletin'].append(formated_pack)
                        self._aprs_msg_sys_new_bn(formated_pack)
                        print(
                            f"aprs Bulletin-MSG fm {aprs_pack['from']} {port_id} - {aprs_pack.get('message_text', '')}")

            elif 'response' in aprs_pack:
                aprs_pack['popt_port_id'] = port_id
                self._handle_response(pack=aprs_pack)

    def _handle_response(self, pack):
        if pack.get('msgNo', False):
            self._handle_ack(pack)

    """
    def check_duplicate_msg(self, aprs_pack, msg_typ: str):
        check_msg_typ = self.ais_aprs_msg_pool[msg_typ]
        for f_msg in check_msg_typ:
            if aprs_pack == f_msg[1][1]:
                return True
        return False
    """

    def _update_pn_msg_gui(self, aprs_pack):
        if self.port_handler is not None:
            if self.port_handler.gui is not None:
                if self.port_handler.gui.aprs_pn_msg_win is not None:
                    self.port_handler.gui.aprs_pn_msg_win.update_tree_single_pack(aprs_pack)

    def _aprs_msg_sys_new_pn(self, formated_pack: (int, (str, dict))):
        self._update_pn_msg_gui(formated_pack)

    @staticmethod
    def _aprs_msg_sys_new_bn(formated_pack: (int, (str, dict))):
        print(
            f"aprs Bulletin-MSG fm {formated_pack[1][1]['from']} {formated_pack[0]} - {formated_pack[1][1].get('message_text', '')}")

    def send_aprs_answer_msg(self, answer_pack, msg='', with_ack=False):
        if answer_pack and msg:
            from_call = answer_pack[1][1].get('addresse', '')
            to_call = answer_pack[1][1].get('from', '')
            if from_call in self.port_handler.ax25_stations_settings:
                # to_call = answer_pack[1][1].get('from', '')
                path = answer_pack[1][1].get('path', [])
                path.reverse()
            elif to_call in self.port_handler.ax25_stations_settings:
                tmp = from_call
                from_call = to_call
                to_call = tmp
                path = answer_pack[1][1].get('path', [])
            else:
                return False
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
                out_pack['is_ack'] = answer_pack[1][1].get('is_ack', False)
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
                pack['message_text'] = f"{el}"
                pack['raw_message_text'] = f":{pack['addresse'].ljust(9)}:{el}" + "{" + f"{int(self._ack_counter)}"
                self._add_to_spooler(pack)
            else:
                pack['message_text'] = f"{el}"
                pack['raw_message_text'] = f":{pack['addresse'].ljust(9)}:{el}"
                self._send_it(pack)
            if not pack.get('is_ack', False):
                # print(f"ECHO {pack}")
                formated_pack = (
                    pack['popt_port_id'],
                    (
                        datetime.now().strftime('%d/%m/%y %H:%M:%S'),
                        pack)

                )
                self.aprs_msg_pool['message'].append(formated_pack)
                self._aprs_msg_sys_new_pn(formated_pack)
        return True

    def _send_it(self, pack):
        if pack['popt_port_id'] == 'I-NET':
            self._send_as_AIS(pack)
        else:
            self._send_as_UI(pack)

    def _add_to_spooler(self, pack):
        # print(f"Spooler in > {pack}")
        pack['N'] = 0
        pack['send_timer'] = 0
        pack['msgNo'] = str(self._ack_counter)
        pack['address_str'] = f"{pack['from']}:{pack['addresse']}"
        self.spooler_buffer[str(self._ack_counter)] = dict(pack)
        self._ack_counter = (self._ack_counter + 1) % 99999

    def _del_fm_spooler(self, pack):
        # print("del_fm_spooler")
        msg_no = pack.get('msgNo', '')
        ack_pack = self.spooler_buffer.get(msg_no, {})
        if ack_pack.get('address_str', '') == f"{pack.get('addresse', '')}:{pack.get('from', '')}":
            # print(f"ACK DEL {msg_no}")
            del self.spooler_buffer[msg_no]
            self._reset_address_in_spooler(pack)

    def _reset_address_in_spooler(self, pack):
        add_str = f"{pack.get('addresse', '')}:{pack.get('from', '')}"
        for msg_no in self.spooler_buffer:
            if self.spooler_buffer[msg_no]['address_str'] == add_str:
                self.spooler_buffer[msg_no]['N'] = 0
                self.spooler_buffer[msg_no]['send_timer'] = 0

    def reset_spooler(self):
        for msg_no in self.spooler_buffer:
            self.spooler_buffer[msg_no]['N'] = 0
            self.spooler_buffer[msg_no]['send_timer'] = 0

    def del_spooler(self):
        self._del_spooler_tr = True

    def _flush_spooler_buff(self):
        self.spooler_buffer = {}

    def _handle_ack(self, pack):
        self._del_fm_spooler(pack)
        self._reset_address_in_spooler(pack)

    def _spooler_task(self):
        send = []
        for msg_no in list(self.spooler_buffer.keys()):
            pack = self.spooler_buffer[msg_no]
            if (pack['address_str'], pack['popt_port_id']) not in send:
                send.append((pack['address_str'], pack['popt_port_id']))
                if pack['send_timer'] < time.time():
                    if pack['N'] < self._parm_max_n:
                        pack['send_timer'] = time.time() + self._parm_resend
                        pack['N'] += 1
                        self._send_it(pack)
                        if pack['N'] == self._parm_max_n:
                            self._del_address_fm_spooler(pack)
                    # else: self.del_fm_spooler(pack, rx=False)

    def _del_address_fm_spooler(self, pack):
        for msg_no in list(self.spooler_buffer.keys()):
            if self.spooler_buffer[msg_no]['address_str'] == pack['address_str']:
                self.spooler_buffer[msg_no]['N'] = self._parm_max_n
                # self.del_fm_spooler(pack, rx=False)

    def _send_as_UI(self, pack):
        port_id = pack.get('popt_port_id', False)
        ax_port = self.port_handler.ax25_ports.get(port_id, False)
        if ax_port:
            path = pack.get('path', [])
            msg_text = pack.get('raw_message_text', '').encode('ASCII', 'ignore')
            from_call = pack.get('from', '')
            add_str = f"{APRS_SW_ID}"
            for elm in path:
                elm = elm.replace('*', '')
                add_str += f" {elm}"
            ax_port.send_UI_frame(
                own_call=from_call,
                add_str=add_str,
                text=msg_text,
                cmd_poll=(False, False)
            )

    def _send_as_AIS(self, pack):
        # print(f"send_as_AIS : {pack}")
        msg = pack['raw_message_text']
        pack_str = f"{pack['from']}>{pack['to']},TCPIP*:{msg}"
        # print(f" AIS OUT > {pack_str}")
        self._ais_tx(pack_str)

    def _send_ack(self, pack_to_resp):
        msg_no = pack_to_resp[1][1].get('msgNo', False)
        if msg_no:
            pack = tuple(pack_to_resp)
            pack[1][1]['is_ack'] = True
            self.send_aprs_answer_msg(pack, f"ack{msg_no}", False)

    """
    def send_rej(self, pack_to_resp):
        pass
    """
    #########################################
    # Beacon Tracer

    def _tracer_build_msg(self):
        # !5251.12N\01109.78E-27.235MHz P.ython o.ther P.acket T.erminal (PoPT)
        _coordinate = decimal_degrees_to_aprs(self.ais_lat, self.ais_lon)
        _aprs_msg = f'!{_coordinate[0]}/{_coordinate[1]}%{APRS_TRACER_COMMENT} #{self.ais_loc}#{str(time.time())}#'
        # _aprs_msg = _aprs_msg.replace('`', '')
        return _aprs_msg

    def tracer_sendit(self):
        print(self._tracer_build_msg())
