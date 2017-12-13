import collections
import time

from iopipe.monotonic import monotonic

Entry = collections.namedtuple('Entry', ['name', 'startTime', 'duration', 'entryType', 'timestamp'])


def time_in_millis(time=None, offset=0):
    if time is None:
        time = monotonic()
    return int((time * 1e9) - offset)


def get_offset(timeline):
    return timeline.offset or timeline.init_time


def mark_data(timeline, name, start_time=None, duration=0, entry_type='mark', timestamp=None):
    data = timeline.data
    use_timestamp = timeline.use_timestamp
    default_time = monotonic()
    entry = Entry(
        name=name,
        startTime=start_time or time_in_millis(default_time, get_offset(timeline)),
        duration=duration,
        entryType=entry_type,
        timestamp=None
    )
    if use_timestamp and entry.timestamp is None:
        entry.timestamp = timestamp or int(time.time() * 1000)
    data.append(entry)
    return data.sort(key=lambda i: i.startTime)


class Timeline(object):
    def __init__(self, offset=0, use_timestamp=False):
        self.init_time = time_in_millis()
        self.data = []
        self.offset = offset
        self.use_timestamp = use_timestamp

    def mark(self, name):
        self.data = mark_data(self, name=name)

    def get_entries(self):
        return self.data

    def get_entries_by_name(self, name):
        return [d for d in self.data if d.name == name]

    def get_entries_by_type(self, type):
        return [d for d in self.data if d.entryType == type]

    def measure(self, name, start, end=None):
        start_mark = self.get_entries_by_name(start)[-1]
        start_time = start_mark.startTime if start_mark else self.init_time - get_offset(self)
        timestamp = start_mark.timestamp if start_mark else None

        end_time = self.now()
        if end is not None:
            end_mark = self.get_entries_by_name(end)[-1]
            end_time = end_mark.startTime if end_mark else end_time

        duration = end_time - start_time

        self.data = mark_data(
            self,
            name=name,
            start_time=start_time,
            duration=duration,
            entry_type='measure',
            timestamp=timestamp
        )

    def clear_marks(self):
        self.data = [d for d in self.data if d['entryType'] != 'mark']

    def clear_measures(self):
        self.data = [d for d in self.data if d['entryType'] != 'measure']

    def clear(self):
        self.data = []

    def now(self):
        return time_in_millis(monotonic(), get_offset(self))
