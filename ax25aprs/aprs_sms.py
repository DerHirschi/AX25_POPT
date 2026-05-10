"""
APRS Short Message Service
"""
import time
from datetime import datetime

from ax25aprs.aprs_dec import parse_aprs_fm_aprsframe, extract_ack, is_cq_call
from ax25aprs.aprs_constant import APRS_SW_ID
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import zeilenumbruch_lines, convert_umlaute_to_ascii


class APRSsms:
    def __init__(self, aprs_main, port_handler):
        logger.info("APRS-SMS: Init")
        self._aprs_main    = aprs_main
        self._port_handler = port_handler

        """ """
        ais_cfg = POPT_CFG.get_CFG_aprs_ais()
        self._spooler_buffer    = {}
        self._del_spooler_tr    = False
        self._ack_counter       = ais_cfg.get('aprs_msg_ack_c', 0)
        self._parm_max_n        = 3
        self._parm_resend       = 60
        self.aprs_msg_pool      = ais_cfg.get('aprs_msg_pool',
                                         {
                                             "message": [],
                                             "bulletin": [],
                                         })
        # Convert old data set
        for arps_msg in self.aprs_msg_pool['message']:
            if arps_msg.get('addresse', ''):
                arps_msg['address'] = str(arps_msg.get('addresse', ''))
                # del arps_msg['addresse']

        self._callbacks = []  # Liste von Callbacks

    # ====================
    def aprs_sms_save(self):
        logger.info("APRS-SMS: Save Conf")

        ais_cfg = POPT_CFG.get_CFG_aprs_ais()
        # APRS-Message
        ais_cfg['aprs_msg_pool'] = dict(self.aprs_msg_pool)
        ais_cfg['aprs_msg_ack_c'] = int(self._ack_counter)
        POPT_CFG.set_CFG_aprs_ais(ais_cfg)

    # ====================
    def aprs_sms_tasker(self):
        # PN MSG Spooler
        if self._del_spooler_tr:
            self._flush_spooler_buff()
            self._del_spooler_tr = False
        self._spooler_task()

    # ====================
    def aprs_sms_rx(self, aprs_pack: dict):
        if not aprs_pack:
            return False
        # APRS PN/BULLETIN MSG
        if aprs_pack.get("format", '') in ['message', 'bulletin', 'thirdparty']:
            self._aprs_msg_sys_rx(aprs_pack=aprs_pack)
            return True
        return False

    # ====================
    def _aprs_msg_sys_rx(self, aprs_pack: {}):
        if aprs_pack.get('format', '') == 'thirdparty':
            # print(f"THP > {aprs_pack['subpacket']}")
            path    = aprs_pack.get('path', [])
            port_id = aprs_pack.get('port_id', '')
            rx_time = aprs_pack.get('rx_time', datetime.now())
            loc     = aprs_pack['locator']
            dist    = aprs_pack['distance']

            aprs_pack               = dict(aprs_pack['subpacket'])
            aprs_pack['path']       = path
            aprs_pack['port_id']    = port_id
            aprs_pack['rx_time']    = rx_time
            aprs_pack['locator']    = loc
            aprs_pack['distance']   = dist
            # aprs_pack['message_text'], ack = extract_ack(aprs_pack.get('message_text', ''))

        if aprs_pack.get('format', '') in ['message', 'bulletin']:
            if aprs_pack.get('msgNo', None) is None:
                aprs_pack['message_text'], aprs_pack['msgNo'] = extract_ack(aprs_pack.get('message_text', ''))
            if 'message_text' in aprs_pack:
                if 'message' == aprs_pack.get('format', ''):
                    if aprs_pack not in self.aprs_msg_pool['message']:
                        self.aprs_msg_pool['message'].append(aprs_pack)
                        self._aprs_msg_sys_new_msg(dict(aprs_pack))
                    if aprs_pack.get('addresse', '') in POPT_CFG.get_stat_CFG_keys():
                        if aprs_pack.get('msgNo', None) is not None:
                            self._send_ack(aprs_pack)
                    self._reset_address_in_spooler(aprs_pack)
                elif 'bulletin' == aprs_pack['format']:
                    if aprs_pack not in self.aprs_msg_pool['bulletin']:
                        self.aprs_msg_pool['bulletin'].append(aprs_pack)
                        self._aprs_msg_sys_new_bn(aprs_pack)
                        logger.debug(f"aprs Bulletin-MSG fm {aprs_pack['from']} {aprs_pack.get('port_id', '')} - {aprs_pack.get('message_text', '')}")

            elif 'response' in aprs_pack:
                # aprs_pack['popt_port_id'] = aprs_pack.get('port_id', '')
                self._handle_response(pack=aprs_pack)

    def _handle_response(self, pack):
        if pack.get('msgNo', False):
            self._handle_ack(pack)

    """
    def check_duplicate_msg(self, aprs_pack, msg_typ: str):
        check_msg_typ = self.ais_aprs_msg_pool[msg_typ]
        for f_msg in check_msg_typ:
            if aprs_pack == f_msg:
                return True
        return False
    """
    # ============================================
    def _update_gui_aprs_msg_win(self, aprs_pack):
        gui = self._port_handler.get_gui()
        if hasattr(gui, 'update_aprs_msg_win'):
            gui.update_aprs_msg_win(aprs_pack)

    def _update_msg_gui(self, aprs_pack: dict):
        if self._port_handler is None:
            return
        # ALARM / NOTY
        if any((aprs_pack.get('addresse', '') in POPT_CFG.get_stat_CFG_keys(),
                aprs_pack.get('from', '') in POPT_CFG.get_stat_CFG_keys(),
                is_cq_call(aprs_pack.get('addresse', ''))
               )):
            if hasattr(self._port_handler, 'set_aprsMailAlarm_PH'):
                self._port_handler.api.set_aprsMailAlarm_PH(True)

        self._update_gui_aprs_msg_win(aprs_pack)

    @staticmethod
    def _aprs_msg_sys_new_bn(aprs_pack: dict):
        try:
            print(f"aprs Bulletin-MSG fm {aprs_pack['from']} {aprs_pack['port_id']} - {aprs_pack.get('message_text', '')}")
        except Exception as ex:
            logger.debug('_aprs_msg_sys_new_bn: Dummy')
            logger.debug(ex)

    # TX-Stuff
    def send_aprs_text_msg(self, answer_pack, msg='', with_ack=False):
        if answer_pack and msg:
            to_call   = str(answer_pack.get('addresse', ''))
            from_call = str(answer_pack.get('from', ''))
            via_call  = str(answer_pack.get('via', ''))
            path      = list(answer_pack.get('path', []))
            if from_call == to_call:
                return False
            port_id = answer_pack.get('port_id', '')
            if not port_id:
                return False
            aprs_str = f"{from_call}>{APRS_SW_ID}"
            new_path = []
            for el in path:
                el: str
                el = el.replace('*', '')
                aprs_str += f",{el}"
                new_path.append(el)
            aprs_str += f"::{to_call.ljust(9)}:dummy"
            out_pack = parse_aprs_fm_aprsframe(aprs_str)
            if out_pack:
                out_pack['from']        = from_call
                out_pack['path']        = new_path
                out_pack['address']     = to_call
                out_pack['addresse']    = to_call
                out_pack['port_id']     = port_id
                out_pack['rx_time']     = datetime.now()
                out_pack['is_ack']      = answer_pack.get('is_ack', False)
                if via_call:
                    out_pack['via'] = via_call
                #print(f"old Path:  {path}")
                #print(f"new Path:  {new_path}")
                #print(f"APRS:  {aprs_str}")
                #print(f"In:    {answer_pack}")
                #print(f"Out:   {out_pack}")
                return self.send_pn_msg(out_pack, msg, with_ack)
            return False
        return False

    def send_pn_msg(self, pack, msg, with_ack=False):
        msg = convert_umlaute_to_ascii(msg)
        msg = zeilenumbruch_lines(msg, max_zeichen=67)
        msg_list = msg.split('\n')

        for el in msg_list:
            if not el or el == '\n':
                continue
            if with_ack:
                pack['message_text'] = f"{el}"
                pack['raw_message_text'] = f":{pack['addresse'].ljust(9)}:{el}" + "{" + f"{int(self._ack_counter)}"
                pack = self._add_to_spooler(pack)
            else:
                pack['message_text'] = f"{el}"
                pack['raw_message_text'] = f":{pack['addresse'].ljust(9)}:{el}"
                self._aprs_main.send_it(dict(pack))
            self._update_gui_aprs_msg_win(pack)
            if not pack.get('is_ack', False):
                self.aprs_msg_pool['message'].append(dict(pack))
                self._aprs_msg_sys_new_msg(dict(pack))
        return True

    def _add_to_spooler(self, pack):
        pack['N']           = 0
        pack['send_timer']  = 0
        pack['msgNo']       = str(self._ack_counter)
        pack['address_str'] = f"{pack.get('from', '')}:{pack.get('addresse', '')}"
        self._spooler_buffer[str(self._ack_counter)] = dict(pack)
        self._ack_counter   = (self._ack_counter + 1) % 99999
        return pack

    def _del_fm_spooler(self, pack):
        msg_no = pack.get('msgNo', '')
        ack_pack = self._spooler_buffer.get(msg_no, {})
        if ack_pack.get('address_str', '') == f"{pack.get('addresse', '')}:{pack.get('from', '')}":
            del self._spooler_buffer[msg_no]
            self._reset_address_in_spooler(pack)
            return True
        return False

    def _reset_address_in_spooler(self, pack):
        add_str = f"{pack.get('addresse', '')}:{pack.get('from', '')}"
        for msg_no in self._spooler_buffer:
            if self._spooler_buffer[msg_no]['address_str'] == add_str:
                self._spooler_buffer[msg_no]['N'] = 0
                self._spooler_buffer[msg_no]['send_timer'] = 0

    def reset_spooler(self):
        for msg_no in self._spooler_buffer:
            self._spooler_buffer[msg_no]['N'] = 0
            self._spooler_buffer[msg_no]['send_timer'] = 0

    def del_spooler(self):
        self._del_spooler_tr = True

    def _flush_spooler_buff(self):
        self._spooler_buffer = {}

    def _handle_ack(self, pack):
        if self._del_fm_spooler(pack):
            self._reset_address_in_spooler(pack)

    def _spooler_task(self):
        send = []
        for msg_no in list(self._spooler_buffer.keys()):
            pack = self._spooler_buffer[msg_no]
            if (pack['address_str'], pack['port_id']) not in send:
                send.append((pack['address_str'], pack['port_id']))
                if pack['send_timer'] < time.time():
                    if pack['N'] < self._parm_max_n:
                        pack['send_timer'] = time.time() + self._parm_resend
                        pack['N'] += 1
                        self._aprs_main.send_it(pack)
                        self._update_gui_aprs_msg_win(pack)
                        if pack['N'] == self._parm_max_n:
                            self._del_address_fm_spooler(pack)
                    # else: self.del_fm_spooler(pack, rx=False)

    def _del_address_fm_spooler(self, pack):
        for msg_no in list(self._spooler_buffer.keys()):
            if self._spooler_buffer[msg_no]['address_str'] == pack['address_str']:
                self._spooler_buffer[msg_no]['N'] = self._parm_max_n
                # self.del_fm_spooler(pack, rx=False)

    def _send_ack(self, pack_to_resp):
        msg_no = pack_to_resp.get('msgNo', False)
        if msg_no:
            pack        = dict(pack_to_resp)
            from_call   = pack.get('addresse', '')
            to_call     = pack.get('from', '')
            path        = pack.get('path', [])
            for call in list(path):
                if call.startswith('WIDE'):
                    path.remove(call)
            path.reverse()
            pack['is_ack']      = True
            pack['address']     = to_call
            pack['addresse']    = to_call
            pack['from']        = from_call
            pack['path']        = path
            self.send_aprs_text_msg(pack, f"ack{msg_no}", False)

    """
    def send_rej(self, pack_to_resp):
        pass
    """
    def get_spooler_buffer(self):
        return self._spooler_buffer

    def get_pn_msg_for_call(self, call: str):
        ret = []
        for arps_msg in self.aprs_msg_pool['message']:
            if arps_msg.get('addresse', '') == call:
                ret.append(arps_msg)
        return ret

    def del_pn_msg_pool(self):
        self.aprs_msg_pool['message'] = []

    def del_bl_msg_pool(self):
        self.aprs_msg_pool['bulletin'] = []

    # ==================================================
    # Callbacks
    def _aprs_msg_sys_new_msg(self, aprs_pack: dict):
        self._update_msg_gui(aprs_pack)
        self._notify_callbacks(aprs_pack)

    def register_callback(self, callback):
        """Callback registrieren (callable)"""
        if callable(callback) and callback not in self._callbacks:
            self._callbacks.append(callback)

    def unregister_callback(self, callback):
        """Callback entfernen"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _notify_callbacks(self, msg: dict):
        """Interne Methode — wird nach Empfang einer neuen Nachricht aufgerufen"""
        for cb in self._callbacks[:]:  # Kopie, falls sich Liste während Aufruf ändert
            try:
                cb(msg)
            except Exception as e:
                logger.error(f"APRS Callback Error: {e}")

