import time
from datetime import datetime

from fnc.str_fnc import get_weekDay_fm_dt


def getNew_schedule_config(intervall: float = 0,
                           move_time: int = 0,
                           minutes=None,
                           hours=None,
                           week_days=None,
                           month=None,
                           month_day=None,
                           set_interval=True,
                           ):
    """
    for minutes_r in range(60):
        minutes[minutes_r] = False
    for hours_r in range(24):
        hours[hours_r] = False
    for week_days_r in ['MO', 'DI', 'MI', 'DO', 'FR', 'SA', 'SO']:
        week_days[week_days_r] = False
    for month_r in range(12):
        month[month_r] = False
    for month_day_r in range(31):
        month_day[month_day_r] = False
    """
    if month_day is None:
        month_day = {}
    if month is None:
        month = {}
    if week_days is None:
        week_days = {}
    if hours is None:
        hours = {}
    if minutes is None:
        minutes = {}
    """
    for week_days_r in ['MO', 'DI', 'MI', 'DO', 'FR', 'SA', 'SO']:
        if week_days_r not in week_days.keys():
            week_days[week_days_r] = False
    """
    return {
        "repeat_min": intervall,        # Float: Minutes. Also needed when 'minutes' not set.
        "move": move_time,              # 0-59 sec
        "minutes": minutes,             # {10: True, 33: True, 57: True}
        "hours": hours,                 # {3: True, 4: True, 12: True}
        "week_days": week_days,         # {'MO'': True, 'DO': True}
        "month": month,                 # {1: True, 11: True}
        "month_day": month_day,         # {18: True, 22: True}
        "set_interval": set_interval,   # False = Trigger after Init + move_time
    }


class PoPTSchedule:
    def __init__(self, conf):
        self.conf = conf
        self._dt_now = datetime.now()
        self._cooldown = time.time()
        self._next_run = 0
        self._month_day_en = False
        self._month_en = False
        self._weekDay_en = False
        self._hour_en = False
        self._min_en = False
        self._rep_min_en = False
        self.re_init()
        if self.conf.get('set_interval', True):
            self._set_intervall()

    def re_init(self):
        self._next_run = 0
        self._month_day_en = self._is_enabled('month_day')
        self._month_en = self._is_enabled('month')
        self._weekDay_en = self._is_enabled('week_days')
        self._hour_en = self._is_enabled('hours')
        self._min_en = self._is_enabled('minutes')
        self._rep_min_en = bool(self.conf.get('repeat_min'))
        self._set_cooldown()

    def _set_cooldown(self):
        self._cooldown = time.time() + 60

    def _set_intervall(self):
        self._next_run = time.time() + (self.conf.get('repeat_min', 1) * 60)

    def manual_trigger(self):
        """ Reset Timers when Task is triggered manual """
        self._set_cooldown()
        self._set_intervall()

    def _is_enabled(self, conf_k):
        for k in self.conf.get(conf_k).keys():
            if self.conf.get(conf_k)[k]:
                return True
        return False

    def _is_month(self):
        return self.conf['month'].get(self._dt_now.month, False)

    def _is_month_day(self):
        return self.conf['month_day'].get(self._dt_now.day, False)

    def _is_weekDay(self):
        return self.conf['week_days'].get(get_weekDay_fm_dt(self._dt_now.weekday()), False)

    def _is_hour(self):
        return self.conf.get('hours').get(self._dt_now.hour, False)

    def _is_minute(self):
        return self.conf.get('minutes').get(self._dt_now.minute, False)

    def _is_sec(self):
        return bool(self.conf.get('move', 0) < self._dt_now.second)

    def _check_month(self):
        if not self._month_en:
            return True
        return self._is_month()

    def _check_month_day(self):
        if not self._month_day_en:
            return True
        return self._is_month_day()

    def _check_weekDays(self):
        if not self._weekDay_en:
            return True
        return self._is_weekDay()

    def _check_hours(self):
        if not self._hour_en:
            return True
        return self._is_hour()

    def _check_minutes(self):
        if not self._min_en:
            return True
        if self._is_minute():
            return self._is_sec()
        return False

    def _check_date(self):
        if any([
            self._month_day_en,
            self._month_en,
            self._weekDay_en,
            self._hour_en,
            self._min_en,
        ]):
            if not self._check_month():
                return False
            if not self._check_month_day():
                return False
            if not self._check_weekDays():
                return False
            if not self._check_hours():
                return False
            if not self._check_minutes():
                return False
            return True
        return False

    def _check_next_run(self):
        if time.time() > self._next_run:
            # print("Next Run Intervall")
            if self._is_sec():
                self._set_intervall()
                return True
        return False

    def _check_intervall(self):
        if any([
            self._month_day_en,
            self._month_en,
            self._weekDay_en,
            self._hour_en,
            self._min_en,
        ]):
            return False
        if not self._rep_min_en:
            return False
        if self._check_next_run():
            return True
        return False

    def _check_schedule(self):
        if time.time() < self._cooldown:
            return False
        self._dt_now = datetime.now()
        if self._check_date():
            if self._check_next_run():
                return True
            return False
        if self._check_intervall():
            return True
        return False

    def is_schedule(self):
        if self._check_schedule():
            self._set_cooldown()
            return True
        return False


if __name__ == '__main__':
    confi = getNew_schedule_config()
    confi['repeat_min'] = 0
    confi['hours'][1] = True
    confi['hours'][0] = True
    confi['hours'][23] = True
    #confi['minutes'][20] = True
    #confi['minutes'][40] = True
    #confi['minutes'][48] = True
    #confi['minutes'][50] = True
    confi['week_days']['DI'] = True
    confi['move'] = 20
    sched = PoPTSchedule(confi)
    while True:
        if sched.is_schedule():
            print(f"Trigger {datetime.now()}")
        # print(f"Rem: {sched.time_until_next_trigger()}")
        time.sleep(1)
