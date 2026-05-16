# TODO/IDEA

from datetime import datetime

from cfg.constant import CFG_data_path
from cli.cli_modulBase import CliModulBase
from fnc.str_fnc import zeilenumbruch
import json
import os


class CliCmdShout(CliModulBase):
    def __init__(self, cli_main):
        super().__init__(cli_main=cli_main)

        self.shout_file  = os.path.join(CFG_data_path, "shoutbox.json")
        self.max_entries = 50  # Letzte Einträge behalten
        self.max_length  = 140  # Zeichen pro Shout

    def _load_shouts(self):
        if os.path.exists(self.shout_file):
            try:
                with open(self.shout_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as ex:
                null = ex
                return []
        return []

    def _save_shouts(self, shouts):
        with open(self.shout_file, 'w', encoding='utf-8') as f:
            json.dump(shouts[-self.max_entries:], f, ensure_ascii=False, indent=2)

    def cmd_shout(self):
        """ //SHOUT Hallo an alle! Tolle Station! 73 de DL1ABC """
        if not self._parameter:
            return "\r # SHOUT <Text>   (max. 140 Zeichen)\r"

        text = b' '.join(self._parameter).decode(self._get_encoding()[0], 'ignore').strip()

        if len(text) > self.max_length:
            text = text[:self.max_length]

        if not text:
            return "\r # Kein Text eingegeben\r"

        shouts = self._load_shouts()

        entry = {
            "time": datetime.now().isoformat(),
            "call": self._to_call_str.split('-')[0],
            "text": text
        }

        shouts.append(entry)
        self._save_shouts(shouts)

        return f"\r # Shoutout gespeichert! Danke {entry['call']} \r"

    def cmd_guestbook(self):
        """ //GUEST [n]  → n = Anzahl Einträge """
        shouts = self._load_shouts()
        if not shouts:
            return "\r # Gästebuch ist noch leer.\r"

        parm = 10
        if self._parameter:
            try:
                parm = int(self._parameter[0])
            except:
                pass

        out = "\r" + "═" * 60 + "\r"
        out += f"     *  Gästebuch / SHOUTBOX  *     ({len(shouts)} Einträge)\r"
        out += "═" * 60 + "\r\r"

        for entry in shouts[-parm:]:
            ts = datetime.fromisoformat(entry['time'])
            time_str = ts.strftime("%d.%m. %H:%M")
            call = entry['call'].ljust(9)

            out += f"{time_str}  {call} > {entry['text']}\r"

        out += "\r" + "═" * 60 + "\r"
        out += "Schreibe mit: //SHOUT Dein Text hier...\r"
        return out