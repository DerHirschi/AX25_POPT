from datetime import datetime

from ax25aprs.aprs_constant import APRS_CQ_ADDRESSES
from ax25aprs.aprs_sms import APRSsms
from cli.cli_modulBase import CliModulBase
from fnc.ax25_fnc import validate_ax25Call


class CliCmdAprsChat(CliModulBase):
    def __init__(self, cli_main):
        super().__init__(cli_main=cli_main)

        self._aprs_chat_port   = 0
        self._aprs_chat_target = 'ALL'
        self._aprs_chat_path   = ['WIDE7-7']  # oder aus Config/UserDB

    # ===========================================
    def cmd_aprs_chat(self):
        self._decode_param(defaults=['ALL', 0])
        target = self._parameter[0].upper()
        try:
            self._aprs_chat_port = int(self._parameter[1])
        except ValueError:
            self._aprs_chat_port = 0

        if target not in APRS_CQ_ADDRESSES and not validate_ax25Call(target):
            return "\r # Ungültiger Call oder Ziel (ALL/CQ)\r"

        self._aprs_chat_target = target
        # self._aprs_chat_path = ['WIDE7-7']  # oder aus Config/UserDB

        self._cliMain.change_cli_state(8)  # Wechsel in Chat-Modus
        # === Callback registrieren ===
        aprs_ais = self._popt_handler.get_aprs_ais()
        if aprs_ais and hasattr(aprs_ais.aprs_sms, 'register_callback'):
            aprs_ais.aprs_sms.register_callback(self._aprs_msg_callback)

        ret = f"\r=== APRS Chat mit {target} auf Port {self._aprs_chat_port} via {' '.join(self._aprs_chat_path)} ===\r"
        ret += "Gib Nachrichten direkt ein. //EXIT zum Verlassen.\r\r"
        ret += self._get_recent_aprs_msgs()  # letzte 3-5 Nachrichten
        return ret

    def cmd_aprs_msgs(self):
        """ //AMSGS [n] """
        self._decode_param(defaults=[15])
        try:
            max_ent = int(self._parameter[0])
        except (ValueError, IndexError):
            max_ent = 15

        aprs_ais = self._popt_handler.get_aprs_ais()
        if not aprs_ais or not hasattr(aprs_ais, 'aprs_sms'):
            return "\r # APRS-SMS Dienst nicht verfügbar.\r"

        sms: APRSsms = aprs_ais.aprs_sms
        my_call = self._to_call_str.split('-')[0]

        # Persönliche Nachrichten + Bulletins/CQ
        personal = sms.get_pn_msg_for_call(my_call)
        all_msgs = sms.aprs_msg_pool.get('message', [])[-50:]   # letzte 50

        out = "\r=== APRS Messages ===\r"
        out += f"{'Time':5} {'From':9} {'To':9} Message\r"
        out += "-" * 70 + "\r"

        shown = 0
        for msg in reversed(all_msgs):        # Neueste zuerst
            if shown >= max_ent:
                break

            ts = msg.get('rx_time', '')
            if isinstance(ts, datetime):
                ts_str = ts.strftime('%H:%M')
            else:
                ts_str = str(ts)[-8:-3] if ' ' in str(ts) else str(ts)

            fr = msg.get('from', '???')[:9]
            to = msg.get('addresse', '???')[:9]
            text = (msg.get('message_text', '') or '').strip()[:48]

            marker = '→' if to == my_call else ' '
            out += f"{ts_str:5} {fr:9}{marker}{to:9} {text}\r"
            shown += 1

        if len(all_msgs) > max_ent:
            out += f"\r... und {len(all_msgs) - max_ent} weitere Nachrichten\r"

        return out + "\r"

    def cmd_aprs_clear(self):
        """ //ACLEAR """
        aprs_ais = self._popt_handler.get_aprs_ais()
        if aprs_ais and hasattr(aprs_ais, 'aprs_sms'):
            # Optional: Nur eigene ungelesene löschen
            aprs_ais.aprs_sms.aprs_msg_pool['message'] = [
                m for m in aprs_ais.aprs_sms.aprs_msg_pool['message']
                if m.get('addresse') != self._to_call_str.split('-')[0]
            ]
            return "\r # APRS-Nachrichten-Liste bereinigt.\r"
        return "\r # Fehler.\r"
    # ===========================================
    def _get_recent_aprs_msgs(self, max_msgs: int = 5):
        """Zeigt die letzten persönlichen + relevanten APRS-Nachrichten"""
        aprs_ais = self._popt_handler.get_aprs_ais()
        if not aprs_ais or not hasattr(aprs_ais, 'aprs_sms'):
            return "\r # APRS-SMS Dienst nicht verfügbar.\r"

        sms: APRSsms = aprs_ais.aprs_sms
        call = self._to_call_str.split('-')[0]  # Dein Call ohne SSID

        msgs = sms.get_pn_msg_for_call(call)

        if not msgs:
            return f"\r # Keine ungelesenen APRS-Nachrichten für {call}.\r"

        out = f"\r--- Letzte APRS-Nachrichten ({len(msgs)}) ---\r"
        for msg in msgs[-max_msgs:]:  # Neueste zuerst
            ts = msg.get('rx_time', '')
            if isinstance(ts, datetime):
                ts = ts.strftime('%H:%M')
            else:
                ts = str(ts)[-8:-3] if len(str(ts)) > 8 else ts

            sender = msg.get('from', '???')
            text = msg.get('message_text', '').strip()[:60]

            # Persönliche Nachrichten hervorheben
            if msg.get('addresse') == call:
                out += f"{ts} {sender:9}> {text}\r"
            else:
                out += f"{ts} {sender:9}  {text}\r"

        out += f"\rAlle Nachrichten mit //AMSGS\r"
        return out
    # ===========================================
    # S8 State
    def s8_aprs_chat(self):
        if not self._raw_input or not self._raw_input.strip():
            return ''

        raw_text = self._raw_input.decode(self._get_encoding()[0], 'ignore').strip()
        text = raw_text.upper()

        # Exit-Befehle
        if text in ('//EXIT', '//Q', '//QUIT', 'EXIT', 'QUIT'):
            self._aprs_chat_cleanup()
            self._cliMain.change_cli_state(1)
            return "\r # APRS Chat beendet.\r" + self._get_ts_prompt()

        if text in ('//H', '//HELP', '//?'):
            return self._aprs_chat_help()

        # Normale CLI-Befehle im Chat-Modus erlauben
        if raw_text.startswith('//'):
            self._cliMain.set_input(self._raw_input)
            return self._cliMain.exec_cmd()

        # ==================== Nachricht senden ====================
        aprs_ais = self._popt_handler.get_aprs_ais()
        if not aprs_ais or not hasattr(aprs_ais, 'aprs_sms'):
            return "\r # APRS-SMS nicht verfügbar!\r"
        from_call = self._to_call_str.split('-')[0]
        dt_now = datetime.now()

        pack = {
            'addresse': self._aprs_chat_target,
            'from':     from_call,
            'port_id':  str(self._aprs_chat_port),
            'path':     self._aprs_chat_path,
            'tx_time':  dt_now
        }
        ack = bool(self._aprs_chat_target not in APRS_CQ_ADDRESSES)
        success = aprs_ais.aprs_sms.send_pn_msg(pack, raw_text, with_ack=ack)
        if success:
            # Echo mit Ziel
            #return (f"{dt_now} [{self._aprs_chat_target}] Port {self._aprs_chat_port} - via: {' '.join(self._aprs_chat_path)}:\r"
            #        f"      [{from_call}] >>> {text}\r")
            # return f"\r[{self._aprs_chat_target}] {raw_text}\r"
            return ""
        else:
            return "\r # Fehler beim Senden der APRS-Nachricht.\r"

    # ===========================================
    @staticmethod
    def _aprs_chat_help():
        """ Interne Hilfe für den APRS-Chat-Modus """
        help_text = (
            "\r\r"
            "=== APRS Chat Hilfe ===\r"
            "--------------------------------------------------\r"
            "  //H          oder //HELP     → Diese Hilfe\r"
            "  //EXIT       oder //Q        → Chat verlassen\r"
            "  //AMSGS [n]                  → Alle Nachrichten anzeigen\r"
            #"  //ACLEAR                     → Gelesene Nachrichten löschen\r"
            "\r"
            "Ziel ändern (ohne Chat zu verlassen):\r"
            "  //ACHAT DL1ABC [Port]        → Mit Station chatten\r"
            "  //ACHAT ALL [Port]           → An alle (Bulletin)\r"
            "  //ACHAT CQ [Port]            → An CQ\r"
            "\r"
            "Tipps:\r"
            "- Nachrichten werden direkt gesendet\r"
            "- Persönliche Nachrichten werden hervorgehoben\r"
            #"- Callback zeigt neue Nachrichten automatisch\r"
            "\r"
        )
        return help_text
    # ===========================================
    def _aprs_msg_callback(self, msg: dict):
        """
        Wird aufgerufen, wenn eine neue APRS-Nachricht eingeht.
        Nur aktiv, wenn wir im Chat-Modus (State 8) sind.
        """
        # Nur reagieren, wenn wir im APRS-Chat sind
        if self._cliMain.state_index != 8:
            return

        # Filter: Nur Nachrichten, die uns betreffen
        my_call = self._to_call_str.split('-')[0]
        target  = msg.get('addresse', '').upper()
        path    = msg.get('path', [])
        sender  = msg.get('from', '')
        port_id = msg.get('port_id', '')

        # Nachricht an uns selbst (persönlich) oder an ALL/CQ wenn wir im ALL-Modus sind
        if not (
            target == my_call or
            (self._aprs_chat_target in APRS_CQ_ADDRESSES and target in APRS_CQ_ADDRESSES) or
            target == self._aprs_chat_target
        ):
            return

        # Nachricht formatieren
        ts = msg.get('rx_time', '') or msg.get('tx_time', '')
        if isinstance(ts, datetime):
            ts_str = ts.strftime('%H:%M')
        else:
            ts_str = str(ts)[-8:-3] if len(str(ts)) > 5 else ts

        text = (msg.get('message_text', '') or '').strip()

        # Ausgabe direkt an den User senden
        if target == my_call or msg.get('tx_time', '') and sender == my_call:
            output = (f"{ts_str} [{target}] Port {port_id} - via: {' '.join(path)}:\r"
                      f"      [{sender}] >>> {text}\r")
        else:
            output = (f"{ts_str} [{target}] Port {port_id} - via: {' '.join(path)}:\r"
                      f"      [{sender}] --: {text}\r")

        # Prompt wieder anzeigen (wichtig im Chat-Modus!)
        #if self._cliMain.can_sidestop and self._user_db_ent.cli_sidestop:
        #    # Bei Sidestop etwas vorsichtiger
        #    output += self._get_ts_prompt()

        self._cliMain.send_output(output, env_vars=False)

    def _aprs_chat_cleanup(self):
        """ Callback wieder entfernen beim Verlassen """
        aprs_ais = self._popt_handler.get_aprs_ais()
        if aprs_ais and hasattr(aprs_ais.aprs_sms, 'unregister_callback'):
            aprs_ais.aprs_sms.unregister_callback(self._aprs_msg_callback)

    # =====================================
    # APRS-Messanger C-Text Noty
    def aprs_cText_noty(self):
        if not self._cliMain.new_aprs_msg_noty:
            return ''
        aprs_ais = self._popt_handler.get_aprs_ais()
        if not hasattr(aprs_ais, 'get_pn_msg_for_call'):
            return ''
        my_aprs_msg = aprs_ais.get_pn_msg_for_call(self._to_call)
        if not my_aprs_msg:
            return ''
        return self._getTabStr_CLI('aprs_new_mail_ctext').format(len(my_aprs_msg))


