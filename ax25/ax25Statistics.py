import time
from collections import deque
from datetime import datetime
from datetime import timedelta

import pickle

from UserDB.UserDBmain import USER_DB
from constant import CFG_mh_data_file, CFG_port_stat_data_file
from fnc.cfg_fnc import cleanup_obj_dict, set_obj_att, set_obj_att_fm_dict
from fnc.socket_fnc import check_ip_add_format
from fnc.str_fnc import conv_time_for_sorting
from fnc.struct_fnc import get_bandwidth_struct, init_day_dic, get_dx_tx_alarm_his_pack


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


class MH:
    def __init__(self):
        print("MH Init")
        mh_load = {}
        self.port_statistik_DB: {int: {str: {}}} = {}
        self.bandwidth = {}

        self.now_min = datetime.now().strftime('%M:%S')[:-1]
        try:
            with open(CFG_mh_data_file, 'rb') as inp:
                mh_load = pickle.load(inp)
        except FileNotFoundError:
            pass
        except EOFError:
            pass
        self.calls: {str: MyHeard} = {}
        for call in mh_load:
            if type(mh_load[call]) == dict:
                self.calls[call] = set_obj_att_fm_dict(new_obj=MyHeard(), input_obj=mh_load[call])
            else:
                self.calls[call] = set_obj_att(new_obj=MyHeard(), input_obj=mh_load[call])
        try:
            with open(CFG_port_stat_data_file, 'rb') as inp:
                self.port_statistik_DB = pickle.load(inp)

        except FileNotFoundError:
            pass
        except EOFError:
            pass

        for call in list(self.calls.keys()):
            for att in dir(MyHeard):
                if not hasattr(self.calls[call], att):
                    setattr(self.calls[call], att, getattr(MyHeard, att))
        self.dx_alarm_trigger = False
        self.last_dx_alarm = time.time()
        self.dx_alarm_hist = []
        self.dx_alarm_perma_hist = {}
        self.parm_new_call_alarm = False
        self.parm_distance_alarm = 50
        self.parm_lastseen_alarm = 1
        self.parm_alarm_ports = []

    def __del__(self):
        pass

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

    def bw_mon_inp(self, ax25_frame, port_id):
        if port_id not in self.port_statistik_DB.keys():
            self.port_statistik_DB[port_id] = {}
        self._init_bw_struct(port_id)
        self._input_stat_db(ax_frame=ax25_frame, port_id=port_id)

    def _input_bw_calc(self, port_id, ax_frame=None, ):
        self._init_bw_struct(port_id=port_id)
        if ax_frame is not None:
            if self.now_min == datetime.now().strftime('%H:%M:%S')[:-1]:
                self.bandwidth[port_id][self.now_min] += len(ax_frame.data_bytes)
            else:
                self.now_min = datetime.now().strftime('%H:%M:%S')[:-1]
                self.bandwidth[port_id][self.now_min] = len(ax_frame.data_bytes)
        else:
            if self.now_min != datetime.now().strftime('%H:%M:%S')[:-1]:
                self.now_min = datetime.now().strftime('%H:%M:%S')[:-1]
                self.bandwidth[port_id][self.now_min] = 0

    def _init_bw_struct(self, port_id):
        if port_id not in self.bandwidth:
            self.bandwidth[port_id] = get_bandwidth_struct()

    def get_bandwidth(self, port_id, baud=1200):
        self._init_bw_struct(port_id=port_id)
        ret = deque([0] * 60, maxlen=60)
        now = datetime.now()
        ten_minutes_ago = now - timedelta(minutes=10)
        minutes = list(self.bandwidth[port_id].keys())
        minutes.reverse()
        ind = minutes.index(now.strftime('%H:%M:%S')[:-1])
        ind2 = minutes.index(ten_minutes_ago.strftime('%H:%M:%S')[:-1])
        new_key_list = minutes[ind:ind2]
        i = 0
        for k in new_key_list:
            byt = int(self.bandwidth[port_id][k])
            f = (((byt * 8) / 10) * 100) / baud
            ret[i] = round(f)
            i += 1
        return ret

    def _input_stat_db(self, ax_frame, port_id):
        now = datetime.now()
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

        self._input_bw_calc(ax_frame=ax_frame, port_id=port_id)
        if date_str not in list(self.port_statistik_DB[port_id].keys()):
            self.port_statistik_DB[port_id][date_str] = init_day_dic()
        self.port_statistik_DB[port_id][date_str][hour]['N_pack'][minute] += 1
        if ax_frame.ctl_byte.flag in self.port_statistik_DB[port_id][date_str][hour]:
            self.port_statistik_DB[port_id][date_str][hour][ax_frame.ctl_byte.flag][minute] += len(ax_frame.data_bytes)
        self.port_statistik_DB[port_id][date_str][hour]['DATA_W_HEADER'][minute] += len(ax_frame.data_bytes)
        self.port_statistik_DB[port_id][date_str][hour]['DATA'][minute] += int(ax_frame.data_len)

    def mh_inp_axip_add(self, ent: '', axip_add: tuple):
        if ent in self.calls.keys():
            self.calls[ent].axip_add = axip_add

    def mh_inp(self, ax25_frame, port_name, port_id, digi=''):
        _dx_alarm = False
        if not digi:
            ########################
            # Port Stat
            if port_id not in self.port_statistik_DB.keys():
                self.port_statistik_DB[port_id] = init_day_dic()
            # self.port_statistik_DB[port_id].input_stat_db(ax_frame=ax25_frame)
            self._input_stat_db(ax25_frame, port_id)
        ########################
        # MH Entry
        if digi:
            call_str = digi
        else:
            call_str = str(ax25_frame.from_call.call_str)
        if call_str not in self.calls.keys():
            ent = MyHeard()
            if self.parm_new_call_alarm:
                _dx_alarm = True
        else:
            ent = self.calls[call_str]



        ent.last_seen = datetime.now()
        ent.own_call = call_str
        ent.pac_n += 1
        ent.port = str(port_name)
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
        _last_digi = ''
        if ax25_frame.via_calls:
            for call in ax25_frame.via_calls:
                if call.c_bit:
                    ent.route.append(str(call.call_str))
                    _last_digi = str(call.call_str)
        if ent.route and digi:
            ent.route = ent.route[:-1]
        if ent.route not in ent.all_routes:
            ent.all_routes.append(list(ent.route))

        # Update AXIP Address
        if ax25_frame.axip_add[0]:
            if ent.axip_add[0]:
                if check_ip_add_format(ent.axip_add[0]):
                    if check_ip_add_format(ax25_frame.axip_add[0]):
                        ent.axip_add = tuple(ax25_frame.axip_add)
            else:
                ent.axip_add = tuple(ax25_frame.axip_add)
        # Get Locator and Distance from User-DB

        db_ent = USER_DB.get_entry(call_str, add_new=True)
        if db_ent:
            ent.locator = str(db_ent.LOC)
            ent.distance = float(db_ent.Distance)

        if not _dx_alarm:
            if self.parm_lastseen_alarm:
                _t_delta = datetime.now() - ent.last_seen
                if self.parm_distance_alarm:
                    if _t_delta.days >= self.parm_lastseen_alarm:
                        if ent.distance >= self.parm_distance_alarm:
                            _dx_alarm = True
                else:
                    if _t_delta.days >= self.parm_lastseen_alarm:
                        _dx_alarm = True
            else:
                if self.parm_distance_alarm:
                    if ent.distance >= self.parm_distance_alarm:
                        _dx_alarm = True
        if _dx_alarm:
            self._set_dx_alarm(ent=ent)
        self.calls[call_str] = ent

        if digi:
            USER_DB.set_typ(call_str=digi, add_new=False, typ='DIGI')
            return
        if _last_digi:
            self.mh_inp(ax25_frame, port_name, port_id, _last_digi)

    def mh_get_data_fm_call(self, call_str):
        if call_str in self.calls.keys():
            return self.calls[call_str]
        return False

    def output_sort_entr(self, n: int = 0):
        """ For MH in Side Panel """
        temp = {}
        self.calls: {str: MyHeard}
        for k in self.calls.keys():
            flag: MyHeard = self.calls[k]
            time_str = conv_time_for_sorting(flag.last_seen)
            temp[time_str] = self.calls[k]
        temp_k = list(temp.keys())
        temp_k.sort()
        temp_k.reverse()
        temp_ret = []
        c = 0
        for k in temp_k:
            temp_ret.append(temp[k])
            c += 1
            if c > n and n:
                break
        return temp_ret

    def get_sort_mh_entry(self, flag_str: str, reverse: bool):
        temp = {}
        self.calls: {str: MyHeard}
        for k in self.calls.keys():
            flag: MyHeard = self.calls[k]

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
            temp[key] = self.calls[k]

        temp_k = list(temp.keys())
        temp_k.sort()
        if not reverse:
            temp_k.reverse()
        temp_ret = {}
        for k in temp_k:
            temp_ret[k] = temp[k]
        return temp_ret

    def mh_get_last_ip(self, call_str: str, param_fail=20):
        if call_str:
            if call_str in self.calls.keys():
                if self.calls[call_str].axip_fail < param_fail:
                    return self.calls[call_str].axip_add
        return '', 0

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

    def mh_ip_failed(self, axip: str):
        for k in self.calls.keys():
            if self.calls[k].axip_add == axip:
                self.calls[k].axip_fail += 1

    def mh_set_ip(self, call: str, axip: (str, int)):
        self.calls[call].axip_add = axip

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

    def save_mh_data(self):
        print('Save MH')
        tmp_mh = cleanup_obj_dict(self.calls)
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


MH_LIST = MH()
