import time
from datetime import datetime

from ax25.ax25Error import AX25EncodingERROR, logger
from ax25.ax25dec_enc import AX25Frame, via_calls_fm_str


class Beacon(object):
    def __init__(self):
        # TODO Load and SAVE to/fm file
        self.text_filename = ''
        self.text = ''
        self.aprs = False
        self.pool = False
        self.is_enabled = False
        self.port_id = 0
        # self.beacon_id = 0
        self.cooldown = time.time()
        self.next_run = time.time()
        self.from_call = 'NOCALL'
        self.to_call = 'NOCALL'
        self.via_calls = ''
        self.ax_frame = AX25Frame()
        self.ax_frame.ctl_byte.UIcByte()
        self.ax_frame.pid_byte.text()
        self.ax_frame.from_call.call_str = self.from_call
        self.ax_frame.to_call.call_str = self.to_call
        self.ax_frame.ctl_byte.cmd = self.aprs
        self.ax_frame.ctl_byte.pf = self.pool
        #################
        # Time Vars
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
                    self.text = f.read().decode('utf-8', 'ignore')
                    print(self.text)
                    return True
            except (FileNotFoundError, EOFError, IsADirectoryError):
                return False

    def set_from_call(self, call: str):
        self.from_call = call

    def set_to_call(self, call: str):
        self.to_call = call

    def set_via_calls(self, calls: str):
        vias = via_calls_fm_str(calls)
        if vias:
            self.ax_frame.via_calls = vias
            self.via_calls = calls

    def encode(self):
        self.set_text_fm_file()
        if self.text:
            self.ax_frame.ctl_byte.cmd = self.aprs
            self.ax_frame.ctl_byte.pf = self.pool
            self.ax_frame.to_call.call = ''
            self.ax_frame.to_call.ssid = 0
            self.ax_frame.to_call.call_str = self.to_call
            self.ax_frame.from_call.call = ''
            self.ax_frame.from_call.ssid = 0
            self.ax_frame.from_call.call_str = self.from_call
            self.ax_frame.data = self.text.encode('UTF-8', 'ignore')
            try:
                self.ax_frame.encode_ax25frame()
            except AX25EncodingERROR:
                logger.error("AX25EncodingERROR: Beacon")
                return False
            return True
        return False

    def is_week_day_enabled(self):
        for k in self.week_days.keys():
            if self.week_days[k]:
                return True
        return False

    def is_month_enabled(self):
        for k in self.month.keys():
            if self.month[k]:
                return True
        return False

    def is_hour_enabled(self):
        for k in self.hours.keys():
            if self.hours[k]:
                return True
        return False

    def is_minutes_enabled(self):
        for k in self.minutes.keys():
            if self.minutes[k]:
                return True
        return False

    def is_hour(self):
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
                hour = now.hour
                minutes = now.minute
                week_day = ['MO', 'DI', 'MI', 'DO', 'FR', 'SA', 'SO'][now.weekday()]
                send_it = False

                if not self.is_hour_enabled() \
                        and not self.is_month_enabled() \
                        and not self.is_week_day_enabled():
                    send_it = True
                elif self.is_month_enabled():
                    if self.is_week_day_enabled():
                        if self.month[month] \
                                and self.week_days[week_day] \
                                and not self.is_hour_enabled():
                            send_it = True
                        elif self.month[month] \
                                and not self.is_hour_enabled():
                            send_it = True
                        elif self.is_hour() \
                                and self.month[month] \
                                and self.week_days[week_day]:
                            send_it = True
                    elif self.is_hour() \
                            and self.month[month]:
                        send_it = True
                elif self.is_week_day_enabled():
                    if self.week_days[week_day]:
                        if self.is_hour_enabled():
                            if self.is_hour():
                                send_it = True
                        else:
                            send_it = True
                elif self.is_hour_enabled():
                    if self.is_hour():
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
