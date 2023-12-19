import time
from datetime import datetime

from ax25.ax25Error import AX25EncodingERROR, logger
from ax25.ax25dec_enc import AX25Frame, via_calls_fm_str
# from ax25.ax25Statistics import MH_LIST
# from ax25.ax25InitPorts import PORT_HANDLER


class Beacon:
    def __init__(self, port_handler=None):
        # TODO Main CFG or better again !
        self._port_handler = port_handler
        self.text_filename = ''
        self.text = ''
        self._text_out = ''
        self.cmd_rpt = False
        self.poll = False
        self.is_enabled = False
        self.port_id = 0
        self.typ = 'Text'
        # self.beacon_id = 0
        self.cooldown = time.time()
        self.next_run = time.time()
        self.from_call = 'NOCALL'
        self.to_call = 'NOCALL'
        self.via_calls = ''
        self.axip_add = ('', 0)
        #################
        # Time Vars TODO change to PoPTSchedule
        self.repeat_time: float = 30.0  # Min
        self.move_time: int = 0  # Sec
        self.minutes: {int: bool} = {}
        self.hours: {int: bool} = {}
        self.week_days: {str: bool} = {}
        self.month: {int: bool} = {}
        for minutes in range(12):  # all 5 Minutes
            self.minutes[minutes] = False
        for hours in range(24):
            self.hours[hours] = False
        for week_days in ['MO', 'DI', 'MI', 'DO', 'FR', 'SA', 'SO']:
            self.week_days[week_days] = False
        for month in range(12):
            self.month[month] = False

        #################

    def re_init(self):
        self.cooldown = time.time() + 60
        self.next_run = time.time() + self.repeat_time

    def set_text_fm_file(self):
        if self.text_filename:
            try:
                with open(self.text_filename, 'rb') as f:
                    self._text_out = f.read().decode('utf-8', 'ignore')
                    # print(self.text)
                    return True
            except (FileNotFoundError, EOFError, IsADirectoryError):
                return False
        return False

    def _set_text_fm_mh(self):
        if not self._port_handler:
            return False
        mh = self._port_handler.get_MH()
        if mh:
            self._text_out = mh.mh_out_beacon(max_ent=12)
            return True
        return False

    def _set_text(self):
        self._text_out = self.text
        return True

    def set_from_call(self, call: str):
        self.from_call = call

    def set_to_call(self, call: str):
        self.to_call = call

    def set_via_calls(self, calls: str):
        _vias = via_calls_fm_str(calls)
        if _vias:
            self.via_calls = calls

    def encode_beacon(self):
        # self.set_text_fm_file()
        _type_handler = {
            'Text': self._set_text,
            'MH': self._set_text_fm_mh,
            'File': self.set_text_fm_file,

        }.get(self.typ, False)
        if not _type_handler:
            return False
        if not _type_handler():
            return False
        if self._text_out:
            _ax_frame = AX25Frame()
            _ax_frame.ctl_byte.UIcByte()
            _ax_frame.pid_byte.text()
            _ax_frame.ctl_byte.cmd = self.cmd_rpt
            _ax_frame.ctl_byte.pf = self.poll
            _ax_frame.to_call.call = ''
            _ax_frame.to_call.ssid = 0
            """
            if self.typ == 'MH':
                _ax_frame.to_call.call_str = "MHEARD"
            else:
            """
            _ax_frame.to_call.call_str = self.to_call
            _ax_frame.from_call.call = ''
            _ax_frame.from_call.ssid = 0
            _ax_frame.from_call.call_str = self.from_call
            _vias = via_calls_fm_str(self.via_calls)
            if _vias:
                _ax_frame.via_calls = _vias
            _ax_frame.axip_add = self.axip_add
            _ax_frame.data = self._text_out.encode('UTF-8', 'ignore')
            try:
                _ax_frame.encode_ax25frame()
            except AX25EncodingERROR:
                logger.error("AX25EncodingERROR: Beacon")
                return False
            return _ax_frame
        return False

    def _is_week_day_enabled(self):
        for k in self.week_days.keys():
            if self.week_days[k]:
                return True
        return False

    def _is_month_enabled(self):
        for k in self.month.keys():
            if self.month[k]:
                return True
        return False

    def _is_hour_enabled(self):
        for k in self.hours.keys():
            if self.hours[k]:
                return True
        return False

    def is_minutes_enabled(self):
        for k in self.minutes.keys():
            if self.minutes[k]:
                return True
        return False

    def _is_hour(self):
        return self.hours[datetime.now().hour]

    """
    TODO
    def is_minute(self):
        minute = datetime.now().minute
        return self.minutes[datetime.now().minute]

    """

    def crone(self):
        """
        for att in dir(self):
            print("{} > {}".format(att, getattr(self, att)))
        """
        if self.is_enabled:
            if time.time() > self.cooldown:
                now = datetime.now()
                month = now.month
                # hour = now.hour
                # minutes = now.minute
                week_day = ['MO', 'DI', 'MI', 'DO', 'FR', 'SA', 'SO'][now.weekday()]
                send_it = False

                if not self._is_hour_enabled() \
                        and not self._is_month_enabled() \
                        and not self._is_week_day_enabled():
                    send_it = True
                elif self._is_month_enabled():
                    if self._is_week_day_enabled():
                        if self.month[month] \
                                and self.week_days[week_day] \
                                and not self._is_hour_enabled():
                            send_it = True
                        elif self.month[month] \
                                and not self._is_hour_enabled():
                            send_it = True
                        elif self._is_hour() \
                                and self.month[month] \
                                and self.week_days[week_day]:
                            send_it = True
                    elif self._is_hour() \
                            and self.month[month]:
                        send_it = True
                elif self._is_week_day_enabled():
                    if self.week_days[week_day]:
                        if self._is_hour_enabled():
                            if self._is_hour():
                                send_it = True
                        else:
                            send_it = True
                elif self._is_hour_enabled():
                    if self._is_hour():
                        send_it = True

                """
                if self.is_hour_enabled():
                    if self.is_hour():
                        send_it = True
                """
                nr = self.next_run + self.move_time
                if time.time() >= nr and send_it:  # !!!!!!!!!!!!
                    self.next_run = (self.repeat_time * 60) + time.time()
                    self.cooldown = time.time() + 60
                    return True
        return False
