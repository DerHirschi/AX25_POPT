from cfg.constant import CLI_TYP_NO_CLI
from cfg.popt_config import POPT_CFG
from cli.cli_modulBase import CliModulBase


class CliCmdStatus(CliModulBase):
    def __init__(self, cli_main):
        super().__init__(cli_main=cli_main)

    # ============================================
    # PORT
    def cmd_port(self):  # TODO Pipe
        ret = f"\r      < {self._getTabStr_CLI('port_overview')} >\r\r"
        ret += "-#--Name----PortTyp----------Stations--Typ------Digi-\r"
        for port_id in self._popt_handler.port_manager.ax25_ports.keys():
            port = self._popt_handler.port_manager.ax25_ports[port_id]
            name = str(port.portname).ljust(7)
            typ = port.port_typ.ljust(15)
            if port.dualPort_primaryPort in [port, None]:

                stations = self._popt_handler.api.get_stat_calls_fm_port(port_id)
                if not stations:
                    stations = ['']
                digi = ''

                if POPT_CFG.get_digi_CFG_for_Call(stations[0]).get('digi_enabled', False) and stations[0]:
                    digi = '(DIGI)'
                if POPT_CFG.get_stat_CFG_fm_call(stations[0]):
                    digi = f"{POPT_CFG.get_stat_CFG_fm_call(stations[0]).get('stat_parm_cli', CLI_TYP_NO_CLI).ljust(7)} " + digi

                ret += f" {str(port_id).ljust(2)} {name} {typ}  {stations[0].ljust(9)} {digi}\r"
                for stat in stations[1:]:
                    digi = ''
                    if POPT_CFG.get_digi_CFG_for_Call(stat).get('digi_enabled', False):
                        digi = '(DIGI)'
                    if POPT_CFG.get_stat_CFG_fm_call(stat):
                        digi = f"{POPT_CFG.get_stat_CFG_fm_call(stat).get('stat_parm_cli', CLI_TYP_NO_CLI).ljust(7)} " + digi
                    ret += f"                             {stat.ljust(9)} {digi}\r"
            else:
                if port.dualPort_primaryPort:
                    ret += f" {str(port_id).ljust(2)} {name} {typ}  Dual-Port: Secondary from Port {port.dualPort_primaryPort.port_id} \r"
        ret += '\r'
        return ret

    # ============================================

    def cmd_lcstatus(self):
        """ Long Connect-Status """
        ret = '\r'
        ret += "--Ch--Port--MyCall----Call------Name----------LOC----QTH-----------Connect\r"
        all_conn = self._popt_handler.get_all_connections()
        for k in all_conn.keys():
            ch = k
            conn = all_conn[k]
            time_start = conn.time_start  # TODO DateSTR
            port_id = conn.own_port.port_id
            my_call = conn.my_call_str
            to_call = conn.to_call_str
            db_ent = conn.user_db_ent
            name = ''
            loc = ''
            qth = ''
            if db_ent:
                name = db_ent.Name
                loc = db_ent.LOC
                qth = db_ent.QTH
            if self._connection.ch_index == ch:
                ret += ">"
            else:
                ret += " "

            ret += f" {str(ch).ljust(3)} " \
                   f"{str(port_id).ljust(3)}   " \
                   f"{my_call.ljust(9)} " \
                   f"{to_call.ljust(9)} " \
                   f"{name.ljust(13)[:13]} " \
                   f"{loc.ljust(6)[:6]} " \
                   f"{qth.ljust(13)[:13]} " \
                   f"{time_start.strftime('%H:%M:%S')}\r"

        return ret + "\r"
