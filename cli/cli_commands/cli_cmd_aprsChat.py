from datetime import datetime

from ax25aprs.aprs_constant import APRS_CQ_ADDRESSES
from ax25aprs.aprs_sms import APRSsms
from cli.cli_modulBase import CliModulBase
from fnc.ax25_fnc import validate_ax25Call
from fnc.str_fnc import zeilenumbruch_lines


class CliCmdAprsChat(CliModulBase):
    def __init__(self, cli_main):
        super().__init__(cli_main=cli_main)

        self._aprs_chat_port        = 0
        self._aprs_chat_target      = 'ALL'
        max_hops                    = 7
        self._aprs_chat_max_hops    = max_hops
        self._aprs_chat_path        = [f'WIDE{max_hops}-{max_hops}']
        # ====================
        self._own_state_id          = 10  # State ID for CLI State Manager

    # ===========================================
    @property
    def own_state_id(self):
        return self._own_state_id

    # ===========================================
    def cmd_aprs_chat(self):
        self._decode_param(defaults=['ALL', 0])
        target = self._parameter[0].upper()
        try:
            self._aprs_chat_port = int(self._parameter[1])
        except ValueError:
            self._aprs_chat_port = 0

        if target not in APRS_CQ_ADDRESSES and not validate_ax25Call(target):
            return "\r" + self._getTabStr_CLI('aprs_chat_invalid_target') + "\r\r"

        self._aprs_chat_target = target

        # Callback registrieren
        aprs_ais = self._popt_handler.get_aprs_ais()
        if aprs_ais and hasattr(aprs_ais.aprs_sms, 'register_callback'):
            aprs_ais.aprs_sms.register_callback(self._aprs_msg_callback)

        path_str = ' '.join(self._aprs_chat_path)

        ret = "\r" + self._getTabStr_CLI('aprs_chat_title').format(
            target, self._aprs_chat_port, path_str) + "\r"

        if self._cliMain.state_index != self._own_state_id:
            ret += self._getTabStr_CLI('aprs_chat_enter') + "\r"
            ret += self._getTabStr_CLI('aprs_chat_help') + "\r\r"
            ret += self._get_recent_aprs_msgs()
            self._cliMain.change_cli_state(self._own_state_id)
        else:
            ret += '\r'

        return ret

    # ===========================================
    def cmd_aprs_msgs(self):
        """ //AMSGS [n] """
        self._decode_param(defaults=[15])
        try:
            max_ent = int(self._parameter[0])
        except (ValueError, IndexError):
            max_ent = 15

        aprs_ais = self._popt_handler.get_aprs_ais()
        if not aprs_ais or not hasattr(aprs_ais, 'aprs_sms'):
            return "\r" + self._getTabStr_CLI('aprs_chat_no_service') + "\r\r"

        sms: APRSsms = aprs_ais.aprs_sms
        my_call = self._to_call_str.split('-')[0]

        all_msgs = sms.aprs_msg_pool.get('message', [])[-50:]

        out = "\n" + self._getTabStr_CLI('aprs_msgs_title') + "\n"
        out += f"{'Time':5} {'From':9} {'To':9} Message\n"
        out += "-" * 70 + "\n"

        shown = 0
        for msg in reversed(all_msgs):
            if shown >= max_ent:
                break
            fr = msg.get('from', '???')
            to = msg.get('addresse', '???')
            if my_call != fr and my_call != to and to not in APRS_CQ_ADDRESSES:
                continue

            ts = msg.get('rx_time', '')
            if isinstance(ts, datetime):
                ts_str = ts.strftime('%H:%M')
            else:
                ts_str = str(ts)[-8:-3] if ' ' in str(ts) else str(ts)

            text = msg.get('message_text', '').strip()

            marker = '>' if to == my_call else ' '
            out += f"{ts_str:5} {fr:9}{marker}{to:9} {text}\n"
            shown += 1

        if len(all_msgs) > max_ent:
            out += "\n" + self._getTabStr_CLI('aprs_msgs_more') + "\n"

        out = zeilenumbruch_lines(out, 79).replace('\n', '\r')
        return out + "\r"

    # ===========================================
    def cmd_aprs_clear(self):
        """ //ACLEAR """
        aprs_ais = self._popt_handler.get_aprs_ais()
        my_call  = self._to_call_str.split('-')[0]
        if aprs_ais and hasattr(aprs_ais, 'aprs_sms'):
            aprs_ais.aprs_sms.aprs_msg_pool['message'] = [
                m for m in aprs_ais.aprs_sms.aprs_msg_pool['message']
                if m.get('addresse') != my_call and
                   m.get('from') != my_call
            ]
            return "\r" + self._getTabStr_CLI('aprs_clear_done') + "\r\r"

        return "\r" + self._getTabStr_CLI('cli_error') + "\r\r"

    # ===========================================
    def _get_recent_aprs_msgs(self, max_msgs: int = 5):
        """ Zeigt die letzten ungelesenen Nachrichten """
        aprs_ais = self._popt_handler.get_aprs_ais()
        if not aprs_ais or not hasattr(aprs_ais, 'aprs_sms'):
            return "\r" + self._getTabStr_CLI('aprs_chat_no_service') + "\r\r"

        sms: APRSsms = aprs_ais.aprs_sms
        call = self._to_call_str.split('-')[0]

        msgs = sms.get_pn_msg_for_call(call)

        if not msgs:
            return "\r" + self._getTabStr_CLI('aprs_recent_no_unread').format(call) + "\r\r"

        out = "\n" + self._getTabStr_CLI('aprs_recent_title').format(len(msgs)) + "\n"

        for msg in msgs[-max_msgs:]:
            ts = msg.get('rx_time', '')
            if isinstance(ts, datetime):
                ts_str = ts.strftime('%H:%M')
            else:
                ts_str = str(ts)[-8:-3] if len(str(ts)) > 8 else ts

            sender = msg.get('from', '???')
            text = msg.get('message_text', '').strip()

            if msg.get('addresse') == call:
                out += f"{ts_str} {sender:9}> {text}\n"
            else:
                out += f"{ts_str} {sender:9}  {text}\n"

        out += "\n" + self._getTabStr_CLI('aprs_recent_all_cmd') + "\n"
        out = zeilenumbruch_lines(out, 79).replace('\n', '\r')
        return out

    # ===========================================
    def aprs_chat_state(self):
        if not self._raw_input:
            return ''

        raw_text: str = self._raw_input.decode(self._get_encoding()[0], 'ignore')
        splited_text = raw_text.upper().strip().split(' ')
        text = splited_text[0]

        # Exit
        if text in ('//EXIT', '//Q', '//QUIT', 'EXIT', 'QUIT'):
            self.aprs_chat_cleanup()
            self._cliMain.change_cli_state(1)
            return "\r" + self._getTabStr_CLI('aprs_chat_exit') + "\r" + self._get_ts_prompt()

        # Hilfe
        if text in ('//H', '//HELP', '//?'):
            return self._aprs_chat_help()

        # WIDE (set max Hops)
        if text in ('//WIDE', '//W', '//WI'):
            if len(splited_text) != 2:
                return "\r" + self._getTabStr_CLI('box_parameter_error') + "\r\r"
            return self._set_hops(splited_text[1])

        # Normale CLI-Befehle im Chat-Modus
        if raw_text.startswith('//'):
            self._cliMain.set_input(self._raw_input)
            return self._cliMain.exec_cmd()

        # Nachricht senden
        raw_text = raw_text.replace('\n', ' ').replace('\r', ' ').strip()
        if not raw_text:
            return ''

        aprs_ais = self._popt_handler.get_aprs_ais()
        if not aprs_ais or not hasattr(aprs_ais, 'aprs_sms'):
            return "\r" + self._getTabStr_CLI('aprs_chat_no_service') + "\r\r"

        from_call = self._to_call_str.split('-')[0]
        #my_call   = self._my_call_str.split('-')[0]
        dt_now    = datetime.now()
        path = [f"{self._my_call_str}*"] + list(self._aprs_chat_path)
        pack = {
            'addresse': self._aprs_chat_target,
            'from':     from_call,
            'port_id':  str(self._aprs_chat_port),
            'path':     path,
            'tx_time':  dt_now
        }
        ack = bool(self._aprs_chat_target not in APRS_CQ_ADDRESSES)
        success = aprs_ais.aprs_sms.send_pn_msg(pack,
                                                raw_text,
                                                with_ack=ack,
                                                digi=True)

        return "" if success else "\r" + self._getTabStr_CLI('aprs_send_error') + "\r\r"

    # ===========================================
    def _set_hops(self, hops: str):
        #self._decode_param(defaults=[7])
        try:
            max_hops = int(hops)
        except (ValueError, IndexError):
            max_hops = 7
        if max_hops not in range(1,8):
            return  "\r" + self._getTabStr_CLI('cli_error') + ": Value: 1 - 7"+ "\r\r"

        self._aprs_chat_max_hops = max_hops
        self._aprs_chat_path     = [f'WIDE{max_hops}-{max_hops}']
        path_str = ' '.join(self._aprs_chat_path)

        ret = ("\r" +
                f" # Max Hops {max_hops} ({f'WIDE{max_hops}-{max_hops}'})\r\r" +
                self._getTabStr_CLI('aprs_chat_title').format(
                self._aprs_chat_target, self._aprs_chat_port, path_str) + "\r")

        return ret

    # ===========================================
    def _aprs_chat_help(self):
        """ Interne Hilfe für den APRS-Chat """
        return (
            "\r\r" +
            self._getTabStr_CLI('aprs_chat_help_title') + "\r" +
            self._getTabStr_CLI('aprs_chat_help_border') + "\r" +
            self._getTabStr_CLI('aprs_chat_help_h') + "\r" +
            self._getTabStr_CLI('aprs_chat_help_max_hops') + "\r" +
            self._getTabStr_CLI('aprs_chat_help_amsgs') + "\r" +
            self._getTabStr_CLI('aprs_chat_help_aclear') + "\r" +
            self._getTabStr_CLI('aprs_chat_help_exit') + "\r\r" +
            self._getTabStr_CLI('aprs_chat_help_achange') + "\r" +
            self._getTabStr_CLI('aprs_chat_help_achat') + "\r\r"
        )

    # ===========================================
    def _aprs_msg_callback(self, msg: dict):
        """ Callback für neue eingehende APRS-Nachrichten """
        if self._cliMain.state_index != self._own_state_id:
            return

        my_call = self._to_call_str.split('-')[0]
        target = msg.get('addresse', '').upper()
        path = msg.get('path', [])
        sender = msg.get('from', '')
        port_id = msg.get('port_id', '')

        if not (
            target == my_call or
            (self._aprs_chat_target in APRS_CQ_ADDRESSES and target in APRS_CQ_ADDRESSES) or
            target == self._aprs_chat_target
        ):
            return

        ts = msg.get('rx_time', '') or msg.get('tx_time', '')
        if isinstance(ts, datetime):
            ts_str = ts.strftime('%H:%M')
        else:
            ts_str = str(ts)[-8:-3] if len(str(ts)) > 5 else ts

        text = msg.get('message_text', '').strip()

        if target == my_call or (msg.get('tx_time') and sender == my_call):
            output = (f"{ts_str} [{target}] Port {port_id} - via: {' '.join(path)}:\n"
                      f"[{sender}]>: {text}\n")
        else:
            output = (f"{ts_str} [{target}] Port {port_id} - via: {' '.join(path)}:\n"
                      f"[{sender}] : {text}\n")

        output = zeilenumbruch_lines(output, 79).replace('\n', '\r')
        output += '\r'
        self._cliMain.send_output(output, env_vars=False)

    # ===========================================
    def aprs_chat_cleanup(self):
        """ Callback aufräumen """
        aprs_ais = self._popt_handler.get_aprs_ais()
        if aprs_ais and hasattr(aprs_ais.aprs_sms, 'unregister_callback'):
            aprs_ais.aprs_sms.unregister_callback(self._aprs_msg_callback)

    # ===========================================
    def aprs_cText_noty(self):
        """ Für C-Text Benachrichtigung """
        if not self._cliMain.new_aprs_msg_noty:
            return ''
        aprs_ais = self._popt_handler.get_aprs_ais()
        if not hasattr(aprs_ais, 'get_pn_msg_for_call'):
            return ''
        my_aprs_msg = aprs_ais.get_pn_msg_for_call(self._to_call)
        if not my_aprs_msg:
            return ''
        return self._getTabStr_CLI('aprs_new_mail_ctext').format(len(my_aprs_msg))

