from collections import deque
from datetime import datetime
from datetime import timedelta

import pickle

from fnc.cfg_fnc import cleanup_obj_dict, set_obj_att
from fnc.socket_fnc import check_ip_add_format
from fnc.str_fnc import conv_time_for_sorting, conv_time_DE_str

mh_data_file = 'data/mh_data.popt'
port_stat_data_file = 'data/port_stat.popt'


def get_time_str():
    return datetime.now().strftime('%d/%m/%y %H:%M:%S')


def get_bandwidth_struct():
    struct = {}
    for m in range(60):
        for s in range(6):
            ts_str = '{}:{}'.format(str(m).zfill(2), s)
            struct[ts_str] = 0
    return struct


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


class MyHeard:
    own_call = ''
    to_calls = []
    route = []
    all_routes = []
    port = ''
    port_id = 0    # Not used yet
    first_seen = datetime.now()
    last_seen = datetime.now()
    pac_n = 0                      # N Packets
    byte_n = 0                     # N Bytes
    h_byte_n = 0                   # N Header Bytes
    rej_n = 0                      # N REJ
    axip_add = '', 0               # IP, Port
    axip_fail = 0                  # Fail Counter


class MH(object):
    def __init__(self):
        print("MH Init")
        mh_load = {}
        self.port_statistik_DB: {int: {str: {}}} = {}
        self.bandwidth = {}

        self.now_min = datetime.now().strftime('%M:%S')[:-1]
        try:
            with open(mh_data_file, 'rb') as inp:
                mh_load = pickle.load(inp)
        except FileNotFoundError:
            pass
        except EOFError:
            pass
        self.calls: {str: MyHeard} = {}
        for call in mh_load:
            self.calls[call] = set_obj_att(new_obj=MyHeard(), input_obj=mh_load[call])

        try:
            with open(port_stat_data_file, 'rb') as inp:
                self.port_statistik_DB = pickle.load(inp)

        except FileNotFoundError:
            pass
        except EOFError:
            pass

        for call in list(self.calls.keys()):
            for att in dir(MyHeard):
                if not hasattr(self.calls[call], att):
                    setattr(self.calls[call], att, getattr(MyHeard, att))

        self.new_call_alarm = False

    def __del__(self):
        pass

    def bw_mon_inp(self, ax25_frame, port_id):
        if port_id not in self.port_statistik_DB.keys():
            self.port_statistik_DB[port_id] = {}
        self.init_bw_struct(port_id)
        self.input_stat_db(ax_frame=ax25_frame, port_id=port_id)

    def input_bw_calc(self, port_id, ax_frame=None, ):
        self.init_bw_struct(port_id=port_id)
        if ax_frame is not None:
            if self.now_min == datetime.now().strftime('%M:%S')[:-1]:
                self.bandwidth[port_id][self.now_min] += len(ax_frame.bytes)
            else:
                self.now_min = datetime.now().strftime('%M:%S')[:-1]
                self.bandwidth[port_id][self.now_min] = len(ax_frame.bytes)
        else:
            if self.now_min != datetime.now().strftime('%M:%S')[:-1]:
                self.now_min = datetime.now().strftime('%M:%S')[:-1]
                self.bandwidth[port_id][self.now_min] = 0

    def init_bw_struct(self, port_id):
        if port_id not in self.bandwidth:
            self.bandwidth[port_id] = get_bandwidth_struct()

    def get_bandwidth(self, port_id, baud=1200):
        self.init_bw_struct(port_id=port_id)
        ret = deque([0] * 100, maxlen=100)
        now = datetime.now()
        ten_minutes_ago = now - timedelta(minutes=10)
        minutes = list(self.bandwidth[port_id].keys())
        minutes.reverse()
        ind = minutes.index(now.strftime('%M:%S')[:-1])
        ind2 = minutes.index(ten_minutes_ago.strftime('%M:%S')[:-1])
        new_key_list = minutes[ind:ind2 + 1]
        i = 0
        for k in new_key_list:
            byt = int(self.bandwidth[port_id][k])
            f = (((byt * 8) / 10) * 100) / baud
            ret[i] = round(f)
            i += 1
        return ret

    def input_stat_db(self, ax_frame, port_id):
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

        self.input_bw_calc(ax_frame=ax_frame, port_id=port_id)
        if date_str not in list(self.port_statistik_DB[port_id].keys()):
            self.port_statistik_DB[port_id][date_str] = init_day_dic()
        self.port_statistik_DB[port_id][date_str][hour]['N_pack'][minute] += 1
        if ax_frame.ctl_byte.flag in self.port_statistik_DB[port_id][date_str][hour]:
            self.port_statistik_DB[port_id][date_str][hour][ax_frame.ctl_byte.flag][minute] += len(ax_frame.bytes)
        self.port_statistik_DB[port_id][date_str][hour]['DATA_W_HEADER'][minute] += len(ax_frame.bytes)
        self.port_statistik_DB[port_id][date_str][hour]['DATA'][minute] += int(ax_frame.data_len)

    def mh_inp_axip_add(self, ent: '', axip_add: tuple):
        if ent in self.calls.keys():
            self.calls[ent].axip_add = axip_add

    def mh_inp(self, ax25_frame, port_name, port_id):
        ########################
        # Port Stat
        if port_id not in self.port_statistik_DB.keys():
            self.port_statistik_DB[port_id] = init_day_dic()
        # self.port_statistik_DB[port_id].input_stat_db(ax_frame=ax25_frame)
        self.input_stat_db(ax25_frame, port_id)
        ########################
        # MH Entry
        call_str = ax25_frame.from_call.call_str
        if call_str not in self.calls.keys():
            self.new_call_alarm = True
            ent = MyHeard()
            ent.first_seen = datetime.now()
        else:
            ent = self.calls[call_str]
        ent.last_seen = datetime.now()
        ent.own_call = call_str
        ent.pac_n += 1
        ent.port = port_name
        ent.port_id = port_id
        ent.byte_n += ax25_frame.data_len
        ent.h_byte_n += len(ax25_frame.bytes) - ax25_frame.data_len
        if ax25_frame.ctl_byte.flag == 'REJ':
            ent.rej_n += 1
        # TO Calls
        to_c_str = ax25_frame.to_call.call_str
        if to_c_str not in ent.to_calls:
            ent.to_calls.append(to_c_str)
        # Routes
        ent.route = []      # Last Route
        if ax25_frame.via_calls:
            for call in ax25_frame.via_calls:
                if call.c_bit:
                    ent.route.append(call.call_str)

        if ent.route not in ent.all_routes:
            ent.all_routes.append(list(ent.route))
        # Update AXIP Address
        if ax25_frame.axip_add[0]:
            if ent.axip_add[0]:
                if check_ip_add_format(ent.axip_add[0]):
                    if check_ip_add_format(ax25_frame.axip_add[0]):
                        ent.axip_add = ax25_frame.axip_add
            else:
                ent.axip_add = ax25_frame.axip_add

        self.calls[call_str] = ent

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

    def output_sort_mh_entr(self, flag_str: str, reverse: bool):
        temp = {}
        self.calls: {str: MyHeard}
        for k in self.calls.keys():
            flag: MyHeard = self.calls[k]
            key: str = {
                'last': conv_time_for_sorting(flag.last_seen),
                'first': conv_time_for_sorting(flag.first_seen),
                'port': str(flag.port_id),
                'call': flag.own_call,
                'pack': str(flag.pac_n),
                'rej': str(flag.rej_n),
                'route': str(max(flag.all_routes)),
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

    def mh_get_ip_fm_all(self, param_fail=20):
        ret: [(str, (str, int))] = []
        for stat_call in self.calls.keys():
            station: MyHeard = self.calls[stat_call]
            if station.axip_add and station.axip_fail < param_fail:
                ent = stat_call, station.axip_add
                ret.append(ent)
        return ret

    def mh_ip_failed(self, axip: str):
        for k in self.calls.keys():
            if self.calls[k].axip_add == axip:
                self.calls[k].axip_fail += 1

    def mh_set_ip(self, call: str, axip: (str, int)):
        self.calls[call].axip_add = axip

    def mh_out_cli(self):
        out = ''
        out += '\r                       < MH - List >\r\r'
        c = 0
        tp = 0
        tb = 0
        rj = 0
        for call in list(self.calls.keys()):

            out += 'P:{:2}>{:5} {:9} {:3}'.format(self.calls[call].port,
                                                  conv_time_DE_str(self.calls[call].last_seen),
                                                  call,
                                                '')

            tp += self.calls[call].pac_n
            tb += self.calls[call].byte_n
            rj += self.calls[call].rej_n
            c += 1
            if c == 2:  # Breite
                c = 0
                out += '\r'
        out += '\r'
        out += '\rTotal Packets Rec.: ' + str(tp)
        out += '\rTotal REJ-Packets Rec.: ' + str(rj)
        out += '\rTotal Bytes Rec.: ' + str(tb)
        out += '\r'

        return out

    def save_mh_data(self):
        print('Save MH')
        tmp_mh = cleanup_obj_dict(self.calls)
        try:
            with open(mh_data_file, 'wb') as outp:
                pickle.dump(tmp_mh, outp, pickle.HIGHEST_PROTOCOL)
        except FileNotFoundError:
            with open(mh_data_file, 'xb') as outp:
                pickle.dump(tmp_mh, outp, pickle.HIGHEST_PROTOCOL)

        try:
            with open(port_stat_data_file, 'wb') as outp:
                pickle.dump(self.port_statistik_DB, outp, pickle.HIGHEST_PROTOCOL)
        except FileNotFoundError:
            with open(port_stat_data_file, 'xb') as outp:
                pickle.dump(self.port_statistik_DB, outp, pickle.HIGHEST_PROTOCOL)


MH_LIST = MH()
