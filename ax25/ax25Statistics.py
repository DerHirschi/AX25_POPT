
import matplotlib.pyplot as plt

from ax25.ax25dec_enc import AX25Frame
from datetime import datetime

import pickle

mh_data_file = 'data/mh_data.popt'
port_stat_data_file = 'data/port_stat.popt'


def get_time_str():
    now = datetime.now()
    return now.strftime('%d/%m/%y %H:%M:%S')


class MyHeard(object):
    def __init__(self):
        self.own_call = ''
        self.to_calls = ["""call_str"""]
        self.route = ''
        self.port = ''
        self.port_id = 0    # Not used yet
        self.first_seen = get_time_str()
        self.last_seen = get_time_str()
        self.pac_n = 1                      # N Packets
        self.byte_n = 0                     # N Bytes
        self.h_byte_n = 0                   # N Header Bytes
        self.rej_n = 0                      # N REJ
        self.axip_add = '', 0               # IP, Port
        self.axip_fail = 0                  # Fail Counter


class PortStatHourStruc(object):
    def __init__(self):
        self.n_packets_hr = {}
        self.I_packets_hr = {}
        self.SABM_packets_hr = {}
        self.DM_packets_hr = {}
        self.DISC_packets_hr = {}
        self.REJ_packets_hr = {}
        self.UI_packets_hr = {}
        self.ALL_data_hr = {}
        self.DATA_data_hr = {}

        for minute in range(60):
            self.n_packets_hr[minute] = 0
            self.I_packets_hr[minute] = 0
            self.SABM_packets_hr[minute] = 0
            self.DM_packets_hr[minute] = 0
            self.DISC_packets_hr[minute] = 0
            self.REJ_packets_hr[minute] = 0
            self.UI_packets_hr[minute] = 0
            self.ALL_data_hr[minute] = 0
            self.DATA_data_hr[minute] = 0


class PortStatDB(object):
    def __init__(self):
        #                   DATE   HOUR
        self.stat_DB_days: {'str': {int: PortStatHourStruc}} = {}
        self.bandwidth = {}
        for m in range(60):
            for s in range(6):
                ts_str = '{}:{}'.format(str(m).zfill(2), s)
                self.bandwidth[ts_str] = 0

        self.now_min = datetime.now().strftime('%M:%S')[:-1]

    def init_day_dic(self):
        ret = {}
        for hour in range(24):
            ret[hour] = PortStatHourStruc()

        return ret

    def input(self, ax_frame: AX25Frame):
        # now = datetime.now().strftime('%d/%m/%y %H:%M:%S')
        self.input_bw_calc(ax_frame=ax_frame)
        now = datetime.now()
        date_str = now.strftime('%d/%m/%y')
        hour = now.hour
        minute = now.minute
        if date_str not in list(self.stat_DB_days.keys()):
            self.stat_DB_days[date_str] = self.init_day_dic()
            """
            if hour in list(self.stat_DB_days[date_str].keys()):
                ent = self.stat_DB_days[date_str][hour]
            else:
                ent = PortStatHourStruc()
                self.stat_DB_days[date_str][hour] = ent
            """

        ent: PortStatHourStruc = self.stat_DB_days[date_str][hour]
        ent.n_packets_hr[minute] += 1
        if ax_frame.ctl_byte.flag == 'I':
            ent.I_packets_hr[minute] += 1
        elif ax_frame.ctl_byte.flag == 'UI':
            ent.UI_packets_hr[minute] += 1
        elif ax_frame.ctl_byte.flag == 'REJ':
            ent.REJ_packets_hr[minute] += 1
        elif ax_frame.ctl_byte.flag == 'SABM':
            ent.REJ_packets_hr[minute] += 1
        elif ax_frame.ctl_byte.flag == 'DM':
            ent.REJ_packets_hr[minute] += 1
        elif ax_frame.ctl_byte.flag == 'DISC':
            ent.REJ_packets_hr[minute] += 1
        ent.ALL_data_hr[minute] += len(ax_frame.bytes)
        ent.DATA_data_hr[minute] += ax_frame.data_len

    def input_bw_calc(self, ax_frame: AX25Frame = None):
        if ax_frame is not None:
            if self.now_min == datetime.now().strftime('%M:%S')[:-1]:
                self.bandwidth[self.now_min] += len(ax_frame.bytes)
            else:
                self.now_min = datetime.now().strftime('%M:%S')[:-1]
                self.bandwidth[self.now_min] = len(ax_frame.bytes)
        else:
            if self.now_min != datetime.now().strftime('%M:%S')[:-1]:
                self.now_min = datetime.now().strftime('%M:%S')[:-1]
                self.bandwidth[self.now_min] = 0

    def plot_test_graph(self, hour: int = 0):
        now = datetime.now()
        date_str = now.strftime('%d/%m/%y')
        hour = now.hour
        _tmp_n_packets = []
        _tmp_I_packets = []
        _tmp_REJ_packets = []
        _tmp_UI_packets = []
        _tmp_ALL_data = []
        _tmp_DATA_data = []
        if date_str in list(self.stat_DB_days.keys()):
            for minute in range(60):
                _tmp_n_packets.append(self.stat_DB_days[date_str][hour].n_packets_hr[minute])
                _tmp_I_packets.append(self.stat_DB_days[date_str][hour].I_packets_hr[minute])
                _tmp_REJ_packets.append(self.stat_DB_days[date_str][hour].REJ_packets_hr[minute])
                _tmp_UI_packets.append(self.stat_DB_days[date_str][hour].UI_packets_hr[minute])
                _tmp_ALL_data.append(self.stat_DB_days[date_str][hour].ALL_data_hr[minute])
                _tmp_DATA_data.append(self.stat_DB_days[date_str][hour].DATA_data_hr[minute])

        """
        for minute in range(60):
           
            _tmp_n_packets.append(random.randrange(0, 30))
            _tmp_I_packets.append(random.randrange(0, 8))
            _tmp_REJ_packets.append(random.randrange(0, 10))
            _tmp_UI_packets.append(random.randrange(0, 10))
            _tmp_ALL_data.append(random.randrange(100, 1500))
            _tmp_DATA_data.append(random.randrange(100, 800))
        print(_tmp_n_packets)
        print(_tmp_I_packets)
        print(_tmp_REJ_packets)
        print(_tmp_UI_packets)
        print(_tmp_ALL_data)
        print(_tmp_DATA_data)
        k = PortStatHourStruc()
        ke = list(k.DATA_data_hr.keys())
        """
        ke = list(range(60))
        # len(ke)
        if _tmp_n_packets:
            plt.plot(ke, _tmp_n_packets, 'g--',
                     ke, _tmp_I_packets, 'y-',
                     ke, _tmp_UI_packets, 'o-',
                     ke, _tmp_REJ_packets, 'r--',
                     )
            #plt.plot(_tmp_n_packets, _tmp_I_packets, _tmp_REJ_packets, _tmp_UI_packets, _tmp_ALL_data, 'ro')
            plt.axis([0, 59, 0, 50])
            plt.legend(['Pakete', 'I-Frames', 'UI-Frames', 'REJ-Frames', ])
            plt.suptitle('Port Statistik')
            plt.show()

    def get_bandwidth(self, baud=1200):
        self.input_bw_calc()
        ret = []
        now = datetime.now().strftime('%M:%S')[:-1]
        minutes = list(self.bandwidth.keys())
        minutes.reverse()
        ind = minutes.index(now)
        new_key_list = minutes[ind:] + minutes[:ind]
        for k in new_key_list:
            byt = int(self.bandwidth[k])
            f = (((byt * 8) / 10) * 100) / baud
            ret.append(f)
        #print(ret)
        #print(len(ret))
        return ret


class MH(object):
    def __init__(self):
        print("MH Init")
        self.calls: {str: MyHeard} = {}
        self.port_statistik_DB: {int: PortStatDB} = {}
        try:
            with open(mh_data_file, 'rb') as inp:
                self.calls = pickle.load(inp)
        except FileNotFoundError:
            pass
        except EOFError:
            pass

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

        """
        self.connections = {
            # conn_id: bla TODO Reverse id 
        }
        """

    def __del__(self):
        pass

    def bw_mon_inp(self, ax25_frame: AX25Frame, port_id):
        if port_id not in self.port_statistik_DB.keys():
            self.port_statistik_DB[port_id] = PortStatDB()

        self.port_statistik_DB[port_id].input(ax_frame=ax25_frame)

    def mh_inp(self, ax25_frame: AX25Frame, port_name, port_id):
        ########################
        # Call Stat
        call_str = ax25_frame.from_call.call_str
        if port_id not in self.port_statistik_DB.keys():
            self.port_statistik_DB[port_id] = PortStatDB()

        self.port_statistik_DB[port_id].input(ax_frame=ax25_frame)
        if call_str not in self.calls.keys():
            ent = MyHeard()
            ent.own_call = call_str
            ent.to_calls.append(ax25_frame.to_call.call_str)
            if ax25_frame.via_calls:
                for call in ax25_frame.via_calls:
                    ent.route += call.call_str
                    if call.call_str != ax25_frame.via_calls[-1].call_str:
                        ent.route += '>'
            else:
                ent.route = []
            ent.port = port_name
            ent.port_id = port_id
            ent.byte_n = ax25_frame.data_len
            ent.h_byte_n = len(ax25_frame.bytes) - ax25_frame.data_len
            if ax25_frame.axip_add[0]:
                ent.axip_add = ax25_frame.axip_add
            if ax25_frame.ctl_byte.flag == 'REJ':
                ent.rej_n = 1
            self.calls[call_str] = ent
        else:
            ent: MyHeard
            ent = self.calls[call_str]
            ent.pac_n += 1
            ent.port = port_name
            ent.port_id = port_id
            ent.byte_n += ax25_frame.data_len
            ent.last_seen = get_time_str()
            to_c_str = ax25_frame.to_call.call_str
            if to_c_str not in ent.to_calls:
                ent.to_calls.append(to_c_str)
            ent.h_byte_n += len(ax25_frame.bytes) - ax25_frame.data_len
            if ax25_frame.ctl_byte.flag == 'REJ':
                ent.rej_n += 1
            self.calls[call_str] = ent

    def mh_get_data_fm_call(self, call_str):
        return self.calls[call_str]

    def output_sort_entr(self, n: int):
        temp = {}
        self.calls: {str: MyHeard}
        for k in self.calls.keys():
            flag: MyHeard = self.calls[k]
            temp[flag.last_seen] = self.calls[k]

        temp_k = list(temp.keys())
        temp_k.sort()
        temp_k.reverse()
        temp_ret = []
        c = 0
        for k in temp_k:

            temp_ret.append(temp[k])
            c += 1
            if c > n:
                break

        return temp_ret

    """
    def mh_get_last_port_obj(self, call_str):
        p_id = self.mh_get_data_fm_call(call_str)
        p_id = p_id['port']
        return config.ax_ports[p_id]
    """

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

    def mh_ip_failed(self, call: str):
        self.calls[call].axip_fail += 1

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
                                                self.calls[call].last_seen,
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
        try:
            with open(mh_data_file, 'wb') as outp:
                # print(self.calls.keys())
                pickle.dump(self.calls, outp, pickle.HIGHEST_PROTOCOL)
        except FileNotFoundError:
            with open(mh_data_file, 'xb') as outp:
                pickle.dump(self.calls, outp, pickle.HIGHEST_PROTOCOL)

        try:
            with open(port_stat_data_file, 'wb') as outp:
                # print(self.calls.keys())
                pickle.dump(self.port_statistik_DB, outp, pickle.HIGHEST_PROTOCOL)
        except FileNotFoundError:
            with open(port_stat_data_file, 'xb') as outp:
                pickle.dump(self.port_statistik_DB, outp, pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    stat = PortStatDB()
    stat.plot_test_graph()
