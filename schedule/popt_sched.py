import time
from datetime import datetime, timedelta

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
    return {
        "repeat_min": int(intervall),
        "move": int(move_time),
        "minutes": dict(minutes),
        "hours": dict(hours),
        "week_days": dict(week_days),
        "month": dict(month),
        "month_day": dict(month_day),
        "set_interval": bool(set_interval),
    }


class PoPTSchedule:
    def __init__(self, conf):
        self.conf = conf
        self._next_run = 0.0
        self._last_trigger = 0.0
        self._month_day_en = False
        self._month_en = False
        self._weekDay_en = False
        self._hour_en = False
        self._min_en = False
        self._has_date_cond = False
        self._rep_min_en = False
        self.re_init()
        self._calc_next_run(initial=self.conf.get('set_interval', True))

    def re_init(self):
        self._next_run = 0.0
        self._last_trigger = 0.0
        self._month_day_en = self._is_enabled('month_day')
        self._month_en = self._is_enabled('month')
        self._weekDay_en = self._is_enabled('week_days')
        self._hour_en = self._is_enabled('hours')
        self._min_en = self._is_enabled('minutes')
        self._rep_min_en = bool(self.conf.get('repeat_min'))
        self._has_date_cond = any([
            self._month_day_en,
            self._month_en,
            self._weekDay_en,
            self._hour_en,
            self._min_en,
        ])

    def manual_trigger(self):
        self._last_trigger = time.time()
        self._calc_next_run()

    def _is_enabled(self, conf_k):
        if not self.conf.get(conf_k):
            return False
        for k in self.conf.get(conf_k).keys():
            if self.conf.get(conf_k)[k]:
                return True
        return False

    def _target_second(self, move):
        if move >= 59:
            return 60
        return move + 1

    def _calc_next_run(self, initial=True):
        now_t = time.time()
        rep_min = self.conf.get('repeat_min', 0)
        move = self.conf.get('move', 0)
        target_sec = self._target_second(move)

        if target_sec >= 60:
            self._next_run = float('inf')
            return

        if not self._has_date_cond:
            if not self._rep_min_en:
                self._next_run = float('inf')
                return
            base = now_t + (rep_min * 60)
            base_dt = datetime.fromtimestamp(base)
            if base_dt.second < target_sec:
                base += target_sec - base_dt.second
            self._next_run = base
            return

        if self._last_trigger > 0.0:
            earliest = max(now_t, self._last_trigger + rep_min * 60)
            next_min_ts = (datetime.fromtimestamp(self._last_trigger)
                           .replace(second=0, microsecond=0)
                           + timedelta(minutes=1)).timestamp()
            if next_min_ts > earliest:
                earliest = next_min_ts
        elif initial:
            earliest = now_t + max(rep_min * 60, 0)
        else:
            earliest = now_t

        dt = datetime.fromtimestamp(earliest).replace(second=0, microsecond=0)

        for _ in range(1051200):
            if self._month_en and not self.conf['month'].get(dt.month, False):
                dt += timedelta(minutes=1)
                continue
            if self._month_day_en and not self.conf['month_day'].get(dt.day, False):
                dt += timedelta(minutes=1)
                continue
            if self._weekDay_en:
                wd = get_weekDay_fm_dt(dt.weekday())
                if not self.conf['week_days'].get(wd, False):
                    dt += timedelta(minutes=1)
                    continue
            if self._hour_en and not self.conf['hours'].get(dt.hour, False):
                dt += timedelta(minutes=1)
                continue
            if self._min_en and not self.conf['minutes'].get(dt.minute, False):
                dt += timedelta(minutes=1)
                continue

            cand = dt.replace(second=target_sec)
            if cand.timestamp() >= earliest:
                self._next_run = cand.timestamp()
                return
            dt += timedelta(minutes=1)

        self._next_run = float('inf')

    def is_schedule(self):
        if self._next_run <= 0:
            return False
        if self._next_run == float('inf'):
            return False
        if time.time() >= self._next_run:
            self._last_trigger = self._next_run
            self._calc_next_run()
            return True
        return False
