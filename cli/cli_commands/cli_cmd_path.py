from cli.cli_modulBase import CliModulBase
from fnc.str_fnc import get_timedelta_CLIstr

class CliCmdPath(CliModulBase):
    def __init__(self, cli_main):
        super().__init__(cli_main=cli_main)
        self._mh = self._popt_handler.get_MH()

    def cmd_path(self):
        if not self._parameter:
            return "\r # PATH <Call> [SHORT|5]\r"

        call = self._parameter[0].decode(self._get_encoding()[0], 'ignore').upper().strip()
        if not call:
            return "\r # Kein Call angegeben\r"

        mode = "ALL"
        max_paths = 10
        if len(self._parameter) > 1:
            p2 = self._parameter[1].decode(self._get_encoding()[0], 'ignore').upper()
            if p2.isdigit():
                max_paths = int(p2)
            elif p2 in ("SHORT", "BEST", "KURZ"):
                mode = "SHORT"

        ent = self._mh.mh_get_data_fm_call(call)   # funktioniert port-unabhängig
        if not ent:
            return f"\r # {call} nicht in MH-Datenbank gefunden.\r"

        out = self._build_path_output(ent, mode, max_paths)
        return out + '\r'


    def _build_path_output(self, ent, mode="ALL", max_paths=10):
        out = f"\rPATH to {ent.own_call}"
        if hasattr(ent, 'locator') and ent.locator:
            out += f" ({ent.locator})"
        out += f" — {len(ent.all_routes)} known paths\r\r"

        out += f"Last seen: {get_timedelta_CLIstr(ent.last_seen)}   "
        out += f"Port: {ent.port_id}   "
        if hasattr(ent, 'distance') and ent.distance > 0:
            out += f"Dist: {int(ent.distance)} km\r\r"

        # Sortiere Pfade nach Länge (kürzeste zuerst)
        sorted_routes = sorted(ent.all_routes, key=len)

        if mode == "SHORT":
            sorted_routes = sorted_routes[:1]   # nur den kürzesten

        dbl_filter = []
        print(sorted_routes)
        for i, route in enumerate(sorted_routes[:max_paths], 1):
            if route in dbl_filter:
                continue
            dbl_filter.append(route)
            hops = len(route)
            path_str = f"{ent.own_call} <─── " + " ─── ".join(route) + f" ─── {self._my_call_str.split('-')[0]}"

            marker = "   " if i > 1 else " ← Best" if hops == len(sorted_routes[0]) else ""

            out += f"{i}. {hops} Hops{marker}\r"
            #out += self._ascii_path_box(path_str, hops)
            out += path_str + '\r'
            out += f"   (letzter Einsatz: {get_timedelta_CLIstr(ent.last_seen)})\r\r"  # könnte man pro Route verbessern

        if len(ent.all_routes) > max_paths:
            out += f"... und {len(ent.all_routes) - max_paths} weitere Pfade\r"

        return out

    @staticmethod
    def _ascii_path_box(path_str: str, hops: int):
        """ Schöne Box """
        width = min(70, len(path_str) + 4)
        box = f"╔{'═' * (width-2)}╗\r"
        box += f"║ {path_str.ljust(width-4)} ║\r"
        box += f"╚{'═' * (width-2)}╝\r"
        return box