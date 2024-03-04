import time
from collections import deque
from datetime import datetime
from datetime import timedelta

import pickle

from UserDB.UserDBmain import USER_DB
from cfg.constant import CFG_mh_data_file, SQL_TIME_FORMAT
from cfg.popt_config import POPT_CFG
from fnc.cfg_fnc import cleanup_obj_dict, set_obj_att, set_obj_att_fm_dict
from fnc.socket_fnc import check_ip_add_format
from fnc.str_fnc import conv_time_for_sorting, conv_time_for_key

"""
def getNew_MyHeard():
    return {
        "own_call": '',
        "to_call": '',
        "route": [],
        "port_id": 0,
        "byte": 0,                  # N Bytes
        "h_byte": 0,                # N Header Bytes
        "type": '',                 # Type: UI/U/RR
        "pid": '',                  # Pack PID
        "axip_add": '',             # IP, Port
        "locator": '',
        "distance": -1,
        "TX": False,
        "first_seen": str(datetime.now().strftime(SQL_TIME_FORMAT)),
        "last_seen": str(datetime.now().strftime(SQL_TIME_FORMAT)),
    }
"""


class MyHeard:
    def __init__(self):
        self.own_call = ''
        self.to_calls = {}
        self.last_dest = ''
        self.route = []
        self.all_routes = []
        self.port = ''
        self.port_id = 0  # Not used yet
        self.first_seen_port = None
        self.first_seen = datetime.now()
        self.last_seen = datetime.now()
        self.pac_n = 0  # N Packets
        self.byte_n = 0  # N Bytes
        self.h_byte_n = 0  # N Header Bytes
        self.rej_n = 0  # N REJ
        self.axip_add = '', 0  # IP, Port
        self.axip_fail = 0  # Fail Counter
        self.locator = ''
        self.distance = -1


def get_dx_tx_alarm_his_pack(
        port_id: int,
        call_str: str,
        via: str,
        path: list,
        locator: str,
        distance: float,
        typ: str,
):
    _now = datetime.now()
    return {
        'ts': _now,
        'port_id': port_id,
        'call_str': call_str,
        'via': via,
        'path': path,
        'loc': locator,
        'dist': distance,
        'typ': typ,
        'key': f"{conv_time_for_key(_now)}{call_str}",

    }


def get_port_stat_struct():
    return {
        'N_pack': 0,
        'I': 0,
        'SABM': 0,
        'DM': 0,
        'DISC': 0,
        'REJ': 0,
        'SREJ': 0,
        'RR': 0,
        'RNR': 0,
        'UI': 0,
        'UA': 0,
        'FRMR': 0,

        'n_I': 0,
        'n_SABM': 0,
        'n_DM': 0,
        'n_DISC': 0,
        'n_REJ': 0,
        'n_SREJ': 0,
        'n_RR': 0,
        'n_RNR': 0,
        'n_UI': 0,
        'n_UA': 0,
        'n_FRMR': 0,

        'DATA_W_HEADER': 0,
        'DATA': 0,
        'time': str(datetime.now().replace(second=0, microsecond=0).strftime(SQL_TIME_FORMAT))
    }


class MH:
    def __init__(self, port_handler):
        print("MH Init")
        self._port_handler = port_handler
        # self._db = None
        self._mh_inp_buffer = []
        self.dx_alarm_trigger = False
        self.last_dx_alarm = time.time()
        self._now_10sec = datetime.now()
        self._now_min = int(datetime.now().minute)
        self._MH_db: {int: {str: MyHeard}} = {}  # MH TODO ? > SQL-DB ?
        self._short_MH = deque([], maxlen=40)
        self._PortStat_buf = {}
        self._bandwidth = {}
        ############################
        # MH
        mh_load = {}
        try:
            with open(CFG_mh_data_file, 'rb') as inp:
                mh_load = pickle.load(inp)
        except (FileNotFoundError, EOFError):
            pass

        if mh_load:
            if type(list(mh_load.keys())[0]) is int:    # New (each Port own MH)
                self._load_MH_new(mh_load)
            else:
                # Load old MH List Format VER < '2.101.4'
                self._load_MH_old(mh_load)

        self._load_MH_update_ent()
        self._init_short_MH()
        ################################
        # Port Statistic
        self._db = None
        ##################
        # Saved Param
        self.dx_alarm_hist = []             # For GUI MH
        self.dx_alarm_perma_hist = {}       # CLI DX List
        self.parm_new_call_alarm = False
        self.parm_distance_alarm = 50
        self.parm_lastseen_alarm = 1
        self.parm_alarm_ports = []
        self._load_fm_cfg()

    def __del__(self):
        pass

    def _load_MH_old(self, mh_load):
        if not mh_load:
            return
        for call in mh_load:
            if type(mh_load[call]) is dict:
                load_ent = set_obj_att_fm_dict(new_obj=MyHeard(), input_obj=mh_load[call])
            else:
                load_ent = set_obj_att(new_obj=MyHeard(), input_obj=mh_load[call])
            port = int(load_ent.port_id)
            if port not in self._MH_db.keys():
                self._MH_db[port] = {}
            self._MH_db[port][call] = load_ent

    def _load_MH_new(self, mh_load):
        if not mh_load:
            return
        for port in list(mh_load.keys()):
            if port not in self._MH_db.keys():
                self._MH_db[port] = {}
            for call in list(mh_load[port].keys()):
                if type(mh_load[port][call]) is dict:
                    if type(mh_load[port][call]['to_calls']) is list:
                        # FIX old MH
                        mh_load[port][call]['to_calls'] = {}
                    self._MH_db[port][call] = set_obj_att_fm_dict(new_obj=MyHeard(), input_obj=mh_load[port][call])
                else:
                    if type(mh_load[port][call].to_calls) is list:
                        # FIX old MH
                        mh_load[port][call].to_calls = {}
                    self._MH_db[port][call] = set_obj_att(new_obj=MyHeard(), input_obj=mh_load[port][call])

    def _load_MH_update_ent(self):
        for port in list(self._MH_db.keys()):
            for call in list(self._MH_db[port].keys()):
                for att in dir(MyHeard):
                    if not hasattr(self._MH_db[port][call], att):
                        setattr(self._MH_db[port][call], att, getattr(MyHeard, att))

    def save_mh_data(self):
        print('Save MH')
        self._save_to_cfg()
        tmp_mh = self._MH_db
        for k in list(tmp_mh.keys()):
            tmp_mh[k] = cleanup_obj_dict(tmp_mh[k])
        try:
            with open(CFG_mh_data_file, 'wb') as outp:
                pickle.dump(tmp_mh, outp, pickle.HIGHEST_PROTOCOL)
        except FileNotFoundError:
            with open(CFG_mh_data_file, 'xb') as outp:
                pickle.dump(tmp_mh, outp, pickle.HIGHEST_PROTOCOL)

    def save_PortStat(self):
        if not self._db:
            return
        for port_id in list(self._PortStat_buf.keys()):
            data_struc: dict = self._PortStat_buf[port_id]
            data_struc['port_id'] = port_id
            self._db.PortStat_insert_data(data_struc)

    ###############################
    # Main CFG/PARAM
    def _load_fm_cfg(self):
        mh_cfg = POPT_CFG.load_CFG_MH()
        self.dx_alarm_hist = mh_cfg.get('dx_alarm_hist', [])
        self.dx_alarm_perma_hist = mh_cfg.get('dx_alarm_perma_hist', {})
        self.parm_new_call_alarm = mh_cfg.get('parm_new_call_alarm', False)
        self.parm_distance_alarm = mh_cfg.get('parm_distance_alarm', 50)
        self.parm_lastseen_alarm = mh_cfg.get('parm_lastseen_alarm', 1)
        self.parm_alarm_ports = mh_cfg.get('parm_alarm_ports', [])

    def _save_to_cfg(self):
        mh_cfg = POPT_CFG.load_CFG_MH()
        mh_cfg['dx_alarm_hist'] = list(self.dx_alarm_hist)
        mh_cfg['dx_alarm_perma_hist'] = dict(self.dx_alarm_perma_hist)
        mh_cfg['parm_new_call_alarm'] = bool(self.parm_new_call_alarm)
        mh_cfg['parm_distance_alarm'] = int(self.parm_distance_alarm)
        mh_cfg['parm_lastseen_alarm'] = int(self.parm_lastseen_alarm)
        mh_cfg['parm_alarm_ports'] = list(self.parm_alarm_ports)
        POPT_CFG.save_CFG_MH(mh_cfg)

    def set_DB(self, sql_db):
        """ called fm PORTHANDLER._init_MH() """
        if not sql_db:
            self._db = None
        self._db = sql_db

    #########################
    # DX Alarm
    def _set_dx_alarm(self, ent):
        port_id = ent.port_id
        if port_id in self.parm_alarm_ports:
            self.dx_alarm_trigger = True
            self.last_dx_alarm = time.time()
            self.dx_alarm_hist.append(ent.own_call)
            self._add_dx_alarm_hist(ent=ent)
            self._port_handler.set_dxAlarm()

    def _add_dx_alarm_hist(self, ent):
        via = ''
        if ent.route:
            via = ent.route[-1]
        hist_struc = get_dx_tx_alarm_his_pack(
            port_id=ent.port_id,
            call_str=ent.own_call,
            via=via,
            path=ent.route,
            locator=ent.locator,
            distance=ent.distance,
            typ='MHEARD',
        )
        self.dx_alarm_perma_hist[str(hist_struc['key'])] = dict(hist_struc)

    def reset_dx_alarm_his(self):
        self.dx_alarm_hist = []
        self.dx_alarm_trigger = False

    ########################
    # Port Statistic
    def _PortStat_input(self, data):
        self._PortStat_check_minute()
        self._PortStat_data_to_var(data=data)

    def _PortStat_check_minute(self):
        if not self._db:
            return
        now_min = int(datetime.now().minute)
        if now_min != self._now_min:
            for port_id in list(self._PortStat_buf.keys()):
                data_struc = dict(self._PortStat_buf[port_id])
                data_struc['port_id'] = port_id
                self._db.PortStat_insert_data(data_struc)
            self._PortStat_buf = {}
            self._now_min = now_min

    def _PortStat_data_to_var(self, data):
        port_id = data.get('port_id', 0)
        ax_frame = data['ax_frame']
        if port_id not in list(self._PortStat_buf.keys()):
            self._PortStat_buf[port_id] = get_port_stat_struct()
        if ax_frame.get('ctl_flag', '') in self._PortStat_buf[port_id].keys():
            flag = ax_frame.get('ctl_flag', '')
            n_flag = f"n_{flag}"
            self._PortStat_buf[port_id][flag] += len(ax_frame.get('ax25_raw', b''))
            self._PortStat_buf[port_id][n_flag] += 1

        self._PortStat_buf[port_id]['N_pack'] += 1
        self._PortStat_buf[port_id]['DATA_W_HEADER'] += len(ax_frame.get('ax25_raw', b''))
        self._PortStat_buf[port_id]['DATA'] += ax_frame.get('payload_len', 0)

    def PortStat_get_data_by_port(self, port_id: int):
        if not self._db:
            return []
        data = self._db.PortStat_get_data_f_port(port_id)
        if data:
            return data
        return []

    def PortStat_reset(self):
        if not self._db:
            return
        self._db.PortStat_delete_data()

    ###################################
    # BW Monitor
    def _input_bw_calc(self, data):
        port_id = data['port_id']
        ax_frame = data['ax_frame']
        now = ax_frame.get('rx_time', datetime.now())
        self._init_bw_struct(port_id=port_id)
        if self._now_10sec.strftime('%M:%S')[:-1] != now.strftime('%M:%S')[:-1]:
            dif: timedelta = now - self._now_10sec
            dif_10 = int(dif.seconds / 10)
            for port_ids in self._bandwidth.keys():
                for i in range(dif_10):
                    self._bandwidth[port_ids].append(0)
            self._now_10sec = now
        self._bandwidth[port_id][-1] += len(ax_frame.get('ax25_raw', b''))
        return

    def _init_bw_struct(self, port_id):
        if port_id not in self._bandwidth:
            self._bandwidth[port_id] = deque([0] * 60, maxlen=60)

    def get_bandwidth(self, port_id, baud=1200):
        ret = []
        now = datetime.now()
        data = list(self._bandwidth.get(port_id, [0] * 60))
        dif: timedelta = now - self._now_10sec
        dif_10 = int(dif.seconds / 10)
        for i in range(dif_10):
            data.append(0)
        data = data[-60:]
        data.reverse()
        for byt in data:
            ret.append(((byt * 80) / baud))
        return ret

    #########################
    # MH Stuff
    def mh_task(self):  # TASKER
        """ Called fm Porthandler Tasker"""
        for el in list(self._mh_inp_buffer):
            if not el.get('tx', False):
                self._PortStat_input(el)
                self._input_bw_calc(el)
                self._mh_inp(el)
            self._mh_inp_buffer = self._mh_inp_buffer[1:]

    def mh_input(self, ax25frame_conf, port_id: int, tx: bool, primary_port_id=-1):
        """ Main Input from ax25Port.gui_monitor()"""
        if tx:
            return
        self._mh_inp_buffer.append({
            'ax_frame': ax25frame_conf,
            'port_id': int(port_id),
            'primary_port_id': int(primary_port_id),
            'tx': bool(tx),
            # 'now': datetime.now(),
        })
        return

    def _mh_inp(self, data, digi=''):
        # TODO Again !
        # inp
        org_port_id = data['port_id']
        primary_port_id = data['primary_port_id']
        if primary_port_id != -1:
            port_id = primary_port_id
        else:
            port_id = org_port_id

        ax25_frame = data['ax_frame']
        dx_alarm = False
        if port_id not in self._MH_db.keys():
            self._MH_db[int(port_id)] = {}
        ########################
        # MH Entry
        if digi:
            call_str = digi
        else:
            call_str = ax25_frame.get('from_call_str', '')
        if not call_str:
            return
        if call_str not in self._MH_db[port_id].keys():
            self._MH_db[port_id][call_str] = MyHeard()
            if self.parm_new_call_alarm:
                dx_alarm = True
        ent = self._MH_db[port_id][call_str]
        ent.last_seen = ax25_frame.get('rx_time', datetime.now())
        ent.own_call = call_str
        ent.pac_n += 1
        if primary_port_id != -1:
            ent.port = f"{primary_port_id}-{org_port_id}"
        else:
            ent.port = f"{org_port_id}"
        ent.port_id = int(port_id)
        if not hasattr(ent, 'first_seen_port'):
            ent.first_seen_port = org_port_id
        elif ent.first_seen_port is None:
            ent.first_seen_port = org_port_id
        ent.byte_n += ax25_frame.get('payload_len', 0)
        ent.h_byte_n += len(ax25_frame.get('ax25_raw', b'')) - ax25_frame.get('payload_len', 0)
        if ax25_frame.get('ctl_flag', '') == 'REJ':
            ent.rej_n += 1
        # Routes
        ent.route = []  # Last Route
        last_digi = ''
        if not digi:
            for call_str, c_bit in ax25_frame.get('via_calls_str_c_bit', []):
                if not c_bit:
                    break
                else:
                    ent.route.append(call_str)
                    last_digi = call_str

        if ent.route not in ent.all_routes:
            ent.all_routes.append(list(ent.route))
        # TO Calls
        to_c_str = ax25_frame.get('to_call_str', '')
        route_key = ','.join(ent.route)
        if to_c_str not in ent.to_calls.keys():
            ent.to_calls[to_c_str] = {route_key: ax25_frame.get('rx_time', datetime.now())}
        else:
            ent.to_calls[to_c_str][route_key] = ax25_frame.get('rx_time', datetime.now())
        ent.last_dest = to_c_str
        # Update AXIP Address
        if ax25_frame.get('axip_add', ('', 0))[0]:
            if ent.axip_add[0]:
                if check_ip_add_format(ax25_frame.get('axip_add', ('', 0))[0]):
                    ent.axip_add = ax25_frame.get('axip_add', ('', 0))
            else:
                ent.axip_add = ax25_frame.get('axip_add', ('', 0))
        # Get Locator and Distance from User-DB
        db_ent = USER_DB.get_entry(call_str, add_new=True)
        if db_ent:
            ent.locator = str(db_ent.LOC)
            ent.distance = float(db_ent.Distance)

        if not dx_alarm:
            if self.parm_distance_alarm and ent.distance != -1:
                if self.parm_lastseen_alarm:
                    t_delta = datetime.now() - ent.last_seen
                    if t_delta.days >= self.parm_lastseen_alarm:
                        if ent.distance >= self.parm_distance_alarm:
                            dx_alarm = True
            else:
                if self.parm_lastseen_alarm:
                    t_delta = datetime.now() - ent.last_seen
                    if t_delta.days >= self.parm_lastseen_alarm:
                        dx_alarm = True

        if dx_alarm:
            self._set_dx_alarm(ent=ent)
        # self._MH_db[port_id][call_str] = ent
        if ent in self._short_MH:
            self._short_MH.remove(ent)
        self._short_MH.append(ent)

        if digi:
            USER_DB.set_typ(call_str=digi, add_new=False, typ='DIGI')
        elif last_digi:
            self._mh_inp(data, last_digi)

    def get_dualPort_lastRX(self, call: str, port_id: int):
        if not call:
            return None
        if port_id not in self._MH_db.keys():
            return None
        ent = self._MH_db.get(port_id, {}).get(call, None)
        if hasattr(ent, 'port'):
            tmp_portID = str(ent.port)
            if '-' not in tmp_portID:
                return None
            portID = tmp_portID.split('-')[-1]
            try:
                return int(portID)
            except ValueError:
                return None
        return None

    def get_dualPort_firstRX(self, call: str, port_id: int):
        if not call:
            return None
        if port_id not in self._MH_db.keys():
            return None
        ent = self._MH_db.get(port_id, {}).get(call, None)
        if hasattr(ent, 'first_seen_port'):
            return ent.first_seen_port
        return None

    def mh_get_data_fm_call(self, call_str, port_id=-1):
        if port_id == -1:
            for port in self._MH_db.keys():
                if call_str in self._MH_db[port].keys():
                    return self._MH_db[port][call_str]
            return False
        else:
            if port_id not in self._MH_db.keys():
                return False
            if call_str in self._MH_db[port_id].keys():
                return self._MH_db[port_id][call_str]
            return False

    def output_sort_entr(self, n: int = 0):
        """ For MH in Side Panel """
        ret = list(self._short_MH)
        ret.reverse()
        return ret[:n]

    def _init_short_MH(self):
        temp = {}
        for port in self._MH_db.keys():
            for k in self._MH_db[port].keys():
                ent = self._MH_db[port][k]
                time_str = conv_time_for_sorting(ent.last_seen)
                if time_str in temp.keys():
                    time_str += '-1'
                temp[time_str] = ent
        temp_k = list(temp.keys())
        temp_k.sort(reverse=True)
        for k in temp_k:
            self._short_MH.appendleft(temp[k])
            if len(self._short_MH) == 40:
                break

    def get_mh_db_by_port(self, port: int):
        return self._MH_db.get(port, {})

    def get_sort_mh_entry(self, flag_str: str, reverse: bool):
        temp = {}
        for port in self._MH_db.keys():
            for k in self._MH_db[port].keys():
                flag = self._MH_db[port][k]

                key: str = {
                    'last': conv_time_for_sorting(flag.last_seen),
                    'first': conv_time_for_sorting(flag.first_seen),
                    'port': str(flag.port_id),
                    'call': flag.own_call,
                    'loc': flag.locator,
                    'dist': str(flag.distance),
                    'pack': str(flag.pac_n),
                    'rej': str(flag.rej_n),
                    'route': str(flag.route),
                    'axip': str(flag.axip_add),
                    'axipfail': str(flag.axip_fail),
                }[flag_str]
                while key in temp.keys():
                    key += '1'
                temp[key] = self._MH_db[port][k]

        temp_k = list(temp.keys())
        temp_k.sort()
        if not reverse:
            temp_k.reverse()
        temp_ret = {}
        for k in temp_k:
            temp_ret[k] = temp[k]
        return temp_ret

    def get_AXIP_fm_DB_MH(self, call_str: str, param_fail=0):
        if not call_str:
            return '', 0
        userdb_axip = USER_DB.get_AXIP(call_str)
        if not param_fail:
            if userdb_axip:
                if userdb_axip[0]:
                    return userdb_axip
        for port in self._MH_db.keys():
            if call_str in self._MH_db[port].keys():
                if call_str in self._MH_db[port].keys():
                    if self._MH_db[port][call_str].axip_add[0]:
                        if self._MH_db[port][call_str].axip_fail < param_fail:
                            if userdb_axip:
                                if userdb_axip[0]:
                                    return userdb_axip
                            return self._MH_db[port][call_str].axip_add
                        if not param_fail:
                            return self._MH_db[port][call_str].axip_add
        return '', 0

    def get_unsort_entrys_fm_port(self, port_id: int):
        return list(self._MH_db.get(port_id, {}).keys())
    """
    def mh_get_last_ip(self, call_str: str, param_fail=0):
        if call_str:
            for port in self._MH_db.keys():
                if call_str in self._MH_db[port].keys():
                    if not param_fail:
                        if self._MH_db[port][call_str].axip_add[0]:
                            return self._MH_db[port][call_str].axip_add
                    elif self._MH_db[port][call_str].axip_fail < param_fail:
                        if self._MH_db[port][call_str].axip_add[0]:
                            return self._MH_db[port][call_str].axip_add
        return '', 0
    """

    """
    def mh_get_ip_fm_all(self, param_fail=20):
        ret: [(str, (str, int))] = []
        for stat_call in self.calls.keys():
            station: MyHeard = self.calls[stat_call]
            if station.axip_add and station.axip_fail < param_fail:
                ent = stat_call, station.axip_add
                ret.append(ent)
        return ret
    """

    def mh_ip_failed(self, axip: str, port_id: int):
        # TODO entry by call_str
        for k in self._MH_db[port_id].keys():
            if self._MH_db[port_id][k].axip_add == axip:
                self._MH_db[port_id][k].axip_fail += 1

    def mh_out_beacon(self, max_ent=12):
        tmp = self.get_sort_mh_entry('last', False)
        ret = ''
        mh_keys = list(tmp.keys())
        n = 0
        for k in mh_keys[:max_ent]:
            if n == 6:
                n = 0
                ret += '\r'
            ret += f"{tmp[k].own_call} "
            n += 1
        return ret

    def reset_mainMH(self):
        self.dx_alarm_trigger = False
        self._MH_db = {}
        self.dx_alarm_hist = []  # For GUI MH
        self.dx_alarm_perma_hist = {}  # CLI DX List

    def reset_dxHistory(self):
        self.dx_alarm_trigger = False
        self.dx_alarm_hist = []  # For GUI MH
        self.dx_alarm_perma_hist = {}  # CLI DX List
# MH_LIST = MH()

