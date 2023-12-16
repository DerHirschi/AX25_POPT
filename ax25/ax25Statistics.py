import time
from collections import deque
from datetime import datetime
from datetime import timedelta

import pickle

from UserDB.UserDBmain import USER_DB
from cfg.constant import CFG_mh_data_file, CFG_port_stat_data_file
from cfg.popt_config import POPT_CFG
from fnc.cfg_fnc import cleanup_obj_dict, set_obj_att, set_obj_att_fm_dict, cleanup_obj_to_dict
from fnc.socket_fnc import check_ip_add_format
from fnc.str_fnc import conv_time_for_sorting, conv_time_for_key
# from sql_db.sql_Error import SQLConnectionError

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


class MyHeard(object):
    own_call = ''
    to_calls = []
    route = []
    all_routes = []
    port = ''
    port_id = 0  # Not used yet
    first_seen = datetime.now()
    last_seen = datetime.now()
    pac_n = 0  # N Packets
    byte_n = 0  # N Bytes
    h_byte_n = 0  # N Header Bytes
    rej_n = 0  # N REJ
    axip_add = '', 0  # IP, Port
    axip_fail = 0  # Fail Counter
    locator = ''
    distance = -1


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


def get_bandwidth_struct():
    _struct = {}
    for _h in range(24):
        for _m in range(60):
            for _s in range(6):
                _ts_str = f'{str(_h).zfill(2)}:{str(_m).zfill(2)}:{_s}'
                _struct[_ts_str] = 0
    return _struct


def get_port_stat_struct():
    struct_hour = {}
    for key in [
        'N_pack',
        'I',
        'SABM',
        'DM',
        'DISC',
        'REJ',
        'RR',
        'RNR',
        'UI',
        'FRMR',
        'DATA_W_HEADER',
        'DATA'
    ]:
        struct_hour[key] = {minute: 0 for minute in range(60)}
    return struct_hour


def init_day_dic():
    ret = {}
    for hour in range(24):
        ret[hour] = get_port_stat_struct()
    return ret


class MH:
    def __init__(self):
        print("MH Init")
        # self._db = None
        self._mh_inp_buffer = []
        self.dx_alarm_trigger = False
        self.last_dx_alarm = time.time()
        self._now_min = datetime.now().strftime('%M:%S')[:-1]
        self._MH_db: {int: {str: MyHeard}} = {}  # MH TODO ? > SQL-DB ?
        self._short_MH = deque([], maxlen=40)
        self.port_statistik_DB: {int: {str: {}}} = {}
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
        ############################
        # Port Statistic
        try:
            with open(CFG_port_stat_data_file, 'rb') as inp:
                self.port_statistik_DB = pickle.load(inp)
        except (FileNotFoundError, EOFError):
            pass

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
                    self._MH_db[port][call] = set_obj_att_fm_dict(new_obj=MyHeard(), input_obj=mh_load[port][call])
                else:
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
        tmp_mh = dict(self._MH_db)
        for k in list(tmp_mh.keys()):
            tmp_mh[k] = cleanup_obj_dict(tmp_mh[k])
        try:
            with open(CFG_mh_data_file, 'wb') as outp:
                pickle.dump(tmp_mh, outp, pickle.HIGHEST_PROTOCOL)
        except FileNotFoundError:
            with open(CFG_mh_data_file, 'xb') as outp:
                pickle.dump(tmp_mh, outp, pickle.HIGHEST_PROTOCOL)

        try:
            with open(CFG_port_stat_data_file, 'wb') as outp:
                pickle.dump(self.port_statistik_DB, outp, pickle.HIGHEST_PROTOCOL)
        except FileNotFoundError:
            with open(CFG_port_stat_data_file, 'xb') as outp:
                pickle.dump(self.port_statistik_DB, outp, pickle.HIGHEST_PROTOCOL)

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

    """
    def set_DB(self, sql_db):
        if not sql_db:
            raise SQLConnectionError
        self._db = sql_db
    """

    #########################
    # DX Alarm
    def _set_dx_alarm(self, ent):
        port_id = ent.port_id
        if port_id in self.parm_alarm_ports:
            self.dx_alarm_trigger = True
            self.last_dx_alarm = time.time()
            self.dx_alarm_hist.append(ent.own_call)
            self._add_dx_alarm_hist(ent=ent)

    def _add_dx_alarm_hist(self, ent):
        _via = ''
        if ent.route:
            _via = ent.route[-1]
        _hist_struc = get_dx_tx_alarm_his_pack(
            port_id=ent.port_id,
            call_str=ent.own_call,
            via=_via,
            path=ent.route,
            locator=ent.locator,
            distance=ent.distance,
            typ='MHEARD',
        )
        self.dx_alarm_perma_hist[str(_hist_struc['key'])] = dict(_hist_struc)

    def reset_dx_alarm_his(self):
        self.dx_alarm_hist = []
        self.dx_alarm_trigger = False

    ########################
    # BW Mon Stuff
    def _bw_mon_inp(self, data):
        port_id = data['port_id']
        if port_id not in self.port_statistik_DB.keys():
            self.port_statistik_DB[port_id] = {}
        # self._init_bw_struct(port_id)
        self._input_stat_db(data=data)

    def _input_bw_calc(self, data):
        port_id = data['port_id']
        ax_frame = data['ax_frame']
        now = data['now']
        self._init_bw_struct(port_id=port_id)
        if self._now_min == now.strftime('%H:%M:%S')[:-1]:
            self._bandwidth[port_id][str(self._now_min)] += len(ax_frame.data_bytes)
            return
        self._now_min = str(now.strftime('%H:%M:%S')[:-1])
        self._bandwidth[port_id][str(self._now_min)] = len(ax_frame.data_bytes)
        return

    def _init_bw_struct(self, port_id):
        if port_id not in self._bandwidth:
            self._bandwidth[port_id] = get_bandwidth_struct()

    def get_bandwidth(self, port_id, baud=1200):
        self._init_bw_struct(port_id=port_id)
        ret = deque([0] * 60, maxlen=60)
        now = datetime.now()
        ten_minutes_ago = now - timedelta(minutes=10)
        minutes = list(self._bandwidth[port_id].keys())
        minutes.reverse()
        ind = minutes.index(now.strftime('%H:%M:%S')[:-1])
        ind2 = minutes.index(ten_minutes_ago.strftime('%H:%M:%S')[:-1])
        new_key_list = minutes[ind:ind2]
        i = 0
        for k in new_key_list:
            byt = int(self._bandwidth[port_id][k])
            f = (((byt * 8) / 10) * 100) / baud
            ret[i] = round(f)
            i += 1
        return ret

    def _input_stat_db(self, data):
        port_id = data['port_id']
        ax_frame = data['ax_frame']
        now = data['now']
        date_str = now.strftime('%d/%m/%y')
        hour = now.hour
        minute = now.minute
        if now.hour == 0:
            last_days = [
                date_str,
                (datetime.now() - timedelta(days=1)).strftime('%d/%m/%y'),
                (datetime.now() - timedelta(days=2)).strftime('%d/%m/%y'),
            ]
            for dt in list(self.port_statistik_DB[port_id].keys()):
                if dt not in last_days:
                    del self.port_statistik_DB[port_id][dt]
        if date_str not in list(self.port_statistik_DB[port_id].keys()):
            self.port_statistik_DB[port_id][date_str] = init_day_dic()
        self.port_statistik_DB[port_id][date_str][hour]['N_pack'][minute] += 1
        if ax_frame.ctl_byte.flag in self.port_statistik_DB[port_id][date_str][hour]:
            self.port_statistik_DB[port_id][date_str][hour][ax_frame.ctl_byte.flag][minute] += len(ax_frame.data_bytes)
        self.port_statistik_DB[port_id][date_str][hour]['DATA_W_HEADER'][minute] += len(ax_frame.data_bytes)
        self.port_statistik_DB[port_id][date_str][hour]['DATA'][minute] += int(ax_frame.data_len)

    #########################
    # MH Stuff
    def mh_task(self):  # TASKER
        """ Called fm Porthandler Tasker"""
        for el in list(self._mh_inp_buffer):
            self._bw_mon_inp(el)
            self._input_bw_calc(el)
            self._mh_inp(el)
            self._mh_inp_buffer = self._mh_inp_buffer[1:]

    def mh_input(self, ax25frame, port_id: int, tx: bool):
        """ Main Input from ax25Port.gui_monitor()"""
        if tx:
            return
        self._mh_inp_buffer.append({
            'ax_frame': ax25frame,
            'port_id': int(port_id),
            # 'tx': bool(tx),
            'now': datetime.now(),
        })
        return

    def _mh_inp(self, data, digi=''):
        # inp
        port_id = data['port_id']
        ax25_frame = data['ax_frame']
        dx_alarm = False
        if port_id not in self._MH_db.keys():
            self._MH_db[int(port_id)] = {}
        ########################
        # MH Entry
        if digi:
            call_str = digi
        else:
            call_str = str(ax25_frame.from_call.call_str)

        if call_str not in self._MH_db[port_id].keys():
            ent = MyHeard()
            if self.parm_new_call_alarm:
                dx_alarm = True
        else:
            ent = self._MH_db[port_id][call_str]
        ent.last_seen = data['now']
        ent.own_call = call_str
        ent.pac_n += 1
        # ent.port = str(port_name)
        ent.port_id = int(port_id)
        ent.byte_n += int(ax25_frame.data_len)
        ent.h_byte_n += len(ax25_frame.data_bytes) - ax25_frame.data_len
        if ax25_frame.ctl_byte.flag == 'REJ':
            ent.rej_n += 1
        # TO Calls
        to_c_str = str(ax25_frame.to_call.call_str)
        if to_c_str not in ent.to_calls:
            ent.to_calls.append(to_c_str)
        # Routes
        ent.route = []  # Last Route
        last_digi = ''
        if ax25_frame.via_calls:
            for call in ax25_frame.via_calls:
                if not call.c_bit:
                    break
                else:
                    ent.route.append(str(call.call_str))
                    last_digi = str(call.call_str)
        if ent.route and digi:
            ent.route = ent.route[:-1]
        if ent.route not in ent.all_routes:
            ent.all_routes.append(list(ent.route))
        # Update AXIP Address
        if ax25_frame.axip_add[0]:
            if ent.axip_add[0]:
                if check_ip_add_format(ax25_frame.axip_add[0]):
                    ent.axip_add = tuple(ax25_frame.axip_add)
            else:
                ent.axip_add = tuple(ax25_frame.axip_add)
        # Get Locator and Distance from User-DB
        db_ent = USER_DB.get_entry(call_str, add_new=True)
        if db_ent:
            ent.locator = str(db_ent.LOC)
            ent.distance = float(db_ent.Distance)

        if not dx_alarm:
            if self.parm_lastseen_alarm:
                _t_delta = datetime.now() - ent.last_seen
                if self.parm_distance_alarm:
                    if _t_delta.days >= self.parm_lastseen_alarm:
                        if ent.distance >= self.parm_distance_alarm:
                            dx_alarm = True
                else:
                    if _t_delta.days >= self.parm_lastseen_alarm:
                        dx_alarm = True
            else:
                if self.parm_distance_alarm:
                    if ent.distance >= self.parm_distance_alarm:
                        dx_alarm = True
        if dx_alarm:
            self._set_dx_alarm(ent=ent)
        self._MH_db[port_id][call_str] = ent
        if ent in self._short_MH:
            self._short_MH.remove(ent)
        self._short_MH.append(ent)

        if digi:
            USER_DB.set_typ(call_str=digi, add_new=False, typ='DIGI')
        elif last_digi:
            self._mh_inp(data, last_digi)

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
        # print(temp_k)
        for k in temp_k:
            print(temp[k].own_call)
            self._short_MH.appendleft(temp[k])
            if len(self._short_MH) == 40:
                break

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
        _tmp = self.get_sort_mh_entry('last', False)
        _ret = ''
        _mh_keys = list(_tmp.keys())
        if len(_mh_keys) > max_ent:
            _mh_keys = _mh_keys[:max_ent]
        _n = 0
        for _k in _mh_keys:
            if _n == 6:
                _n = 0
                _ret += '\r'
            _ret += f"{_tmp[_k].own_call} "
            _n += 1
        return _ret


# MH_LIST = MH()

