import time
from datetime import datetime

from ax25.ax25Error import AX25EncodingERROR, logger
from ax25.ax25dec_enc import AX25Frame, via_calls_fm_str


class Beacon:
    def __init__(self):
        self.text_filename = ''
        self.text = ''
        self.aprs = False
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
        #################
        # Time Vars
        self.repeat_time: float = 30.0  # Min
        self.move_time: int = 0  # Sec
        self.minutes: {int: bool} = {}
        self.hours: {int: bool} = {}
        self.week_days: {str: bool} = {}
        self.month: {int: bool} = {}
        for minutes in range(12):   # all 5 Minutes
            self.minutes[minutes] = False
        for hours in range(24):
            self.hours[hours] = False
        for week_days in ['MO', 'DI', 'MI', 'DO', 'FR', 'SA', 'SO']:
            self.week_days[week_days] = False
        for month in range(12):
            self.month[month] = False

        #################
    def re_init(self):
        self.cooldown = time.time()
        self.next_run = time.time()

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
            self.ax_frame.to_call.call = ''
            self.ax_frame.to_call.ssid = 0
            self.ax_frame.to_call.call_str = self.to_call
            self.ax_frame.from_call.call = ''
            self.ax_frame.from_call.ssid = 0
            self.ax_frame.from_call.call_str = self.from_call
            self.ax_frame.data = self.text.encode('UTF-8', 'ignore')
            try:
                self.ax_frame.encode()
            except AX25EncodingERROR:
                logger.error("AX25EncodingERROR: Beacon")
                return False
            return True
        return False

    def crone(self):
        """
        for att in dir(self):
            print("{} > {}".format(att, getattr(self, att)))
        """
        if self.is_enabled:
            if time.time() > self.cooldown:
                now = datetime.now()
                # now_min = int(now.strftime("%M"))
                nr = self.next_run + self.move_time
                if time.time() >= nr:   # !!!!!!!!!!!!
                    self.next_run = (self.repeat_time * 60) + time.time()
                    self.cooldown = time.time() + 60
                    return True
        return False
