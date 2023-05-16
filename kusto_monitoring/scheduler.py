import logging
import time

from typing import Callable
from datetime import datetime, timedelta
from multiprocessing.pool import ThreadPool


class WildcardMatch(set):
    def __contains__(self, item):
        return True


_wildcard = WildcardMatch()


def _parse_crontab_element(s: str) -> set:
    if s == "*":
        return _wildcard
    return set([int(e) for e in s.split(",")])


class Schedule(object):
    def __init__(self, s: str):
        parts = s.strip().split()
        if len(parts) != 5:
            raise Exception(f"crontab format is not recognized: '{s}'")
        self.mins = _parse_crontab_element(parts[0])
        self.hours = _parse_crontab_element(parts[1])
        self.days = _parse_crontab_element(parts[2])
        self.months = _parse_crontab_element(parts[3])
        self.dow = _parse_crontab_element(parts[4])

    def matches(self, t) -> bool:
        return (
            (t.minute in self.mins)
            and (t.hour in self.hours)
            and (t.day in self.days)
            and (t.month in self.months)
            and (t.weekday() in self.dow)
        )


class Task(object):
    def __init__(self, name, schedule: str, action: Callable, *args, **kwargs):
        self.name = name
        self.schedule = Schedule(schedule)
        self.action = action
        self.args = args
        self.kwargs = kwargs

    def should_run(self, t) -> bool:
        return self.schedule.matches(t)

    def run(self):
        logging.info(f"Running task '{self.name}'")
        try:
            self.action(*self.args, **self.kwargs)
        except:
            logging.exception("")


class Scheduler(object):
    def __init__(self, tasks):
        self.tasks = tasks
        self.stopping = False

    def stop(self):
        self.stopping = True

    def run(self):
        with ThreadPool() as pool:
            t = datetime(*datetime.now().timetuple()[:5])
            while not self.stopping:
                for task in self.tasks:
                    if task.should_run(t):
                        pool.apply_async(task.run)
                t += timedelta(minutes=1)
                now = datetime.now()
                if now < t:
                    time.sleep((t - now).seconds)
