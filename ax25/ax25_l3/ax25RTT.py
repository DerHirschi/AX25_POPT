import time


class RTT:
    # TODO
    def __init__(self, connection):
        self._conn = connection
        self._act_paclen = self._conn.parm_PacLen
        self.rtt_dict: {int: float} = {}
        self.rtt_best = 999.0
        self.rtt_worst = 0.0
        self.rtt_average = float(self._conn.IRTT / 1000) / 2
        self.rtt_last = 0.0
        self.rtt_single_timer = 0.0
        for i in range(8):
            self.rtt_dict[i] = {
                'timer': 0.0,
                'paclen': int(self._act_paclen),
                'rtt': self.rtt_average
            }
        # self.rtt_single_list = [float(self.rtt_average)]*4
        self.rtt_single_list = []

    def get_rtt_avrg(self):
        self._calc_rtt_vars()
        if self.rtt_best == 999:
            return self.rtt_average
        else:
            return (self.rtt_average + self.rtt_best) / 2

    def set_rtt_timer(self, vs: int, paclen: int):
        self.rtt_dict[vs]['timer'] = time.time()
        self.rtt_dict[vs]['paclen'] = paclen
        # print('set {}'.format(self.rtt_dict))

    def set_rtt_single_timer(self):
        self.rtt_single_timer = time.time()

    def rtt_single_rx(self, stop=False):
        if stop:
            self.rtt_single_timer = 0.0
        if self.rtt_single_timer:
            # rtt = float(((time.time() - self.rtt_single_timer) / 2) / 16) * self.act_paclen
            rtt = (time.time() - self.rtt_single_timer) * 1.3
            self.rtt_single_list[0] = rtt
            self.rtt_single_list = self.rtt_single_list[1:] + [self.rtt_single_list[0]]
            self.rtt_single_timer = 0.0
        # print("RTT-S: {}".format(self.rtt_single_list))

    def rtt_rx(self, vs: int):
        # print('RX {}' .format(self.rtt_dict))
        timer = float(self.rtt_dict[vs]['timer'])
        if timer:
            self.rtt_dict[vs]['rtt'] = time.time() - timer
        self.rtt_last = float(self.rtt_dict[vs]['rtt'])
        self._calc_rtt_vars()
        # print('RX rtt_last {}'.format(self.rtt_last))
        # print('RX rtt_best {}'.format(self.rtt_best))
        # print('RX rtt_worst {}'.format(self.rtt_worst))
        # print('RX rtt_average {}'.format(self.rtt_average))
        return self.rtt_last

    def _calc_rtt_vars(self):
        # print('_________calc_rtt____________')
        self.rtt_best = min(self.rtt_last, self.rtt_best)
        self.rtt_worst = max(self.rtt_last, self.rtt_worst)
        tmp = list(self.rtt_single_list)
        # print("tmp: {}".format(tmp))
        for vs in self.rtt_dict.keys():
            if self.rtt_dict[vs]['rtt']:
                # tmp_len = self.rtt_dict[vs]['paclen'] + 16
                # rtt = float((self.rtt_dict[vs]['rtt'] / 2) / tmp_len) * self.act_paclen
                rtt = self.rtt_dict[vs]['rtt']
                # print("rtt: {}".format(tmp))
                tmp.append(rtt)
        self.rtt_average = sum(tmp) / len(tmp)

        # print("rtt_average: {}".format(self.rtt_average))
        # print('------------------------')
