import collections
import time

from iopipe.monotonic import monotonic

Entry = collections.namedtuple(
    "Entry", ["name", "startTime", "duration", "entryType", "timestamp"]
)


def time_in_millis(time=None, offset=0):
    if time is None:
        time = monotonic()
    return time * 1000 - offset


def get_offset(timeline):
    return timeline.offset or timeline.init_time


def mark_data(
    timeline, name, start_time=None, duration=0, entry_type="mark", timestamp=None
):
    data = timeline.data or []
    entry = Entry(
        name=name,
        startTime=start_time or time_in_millis(offset=get_offset(timeline)),
        duration=duration,
        entryType=entry_type,
        timestamp=timestamp or int(time.time() * 1000),
    )
    data.append(entry)
    data.sort(key=lambda i: i.startTime)
    return data, entry


class Timeline(object):
    def __init__(self, offset=0):
        self.init_time = time_in_millis()
        self.offset = offset
        self.data = []

    def mark(self, name):
        self.data, entry = mark_data(self, name=name)
        return entry

    def get_entries(self):
        return self.data

    def get_entries_by_name(self, name):
        return [d for d in self.data if d.name == name]

    def get_entries_by_type(self, type):
        return [d for d in self.data if d.entryType == type]

    def measure(self, name, start, end=None):
        start_mark = self.get_entries_by_name(start)
        start_mark = start_mark[-1] if start_mark else None
        start_time = (
            start_mark.startTime if start_mark else self.init_time - get_offset(self)
        )
        timestamp = start_mark.timestamp if start_mark else None

        end_time = self.now()
        if end is not None:
            end_mark = self.get_entries_by_name(end)
            end_mark = end_mark[-1] if end_mark else None
            end_time = end_mark.startTime if end_mark else end_time

        duration = end_time - start_time

        self.data, entry = mark_data(
            self,
            name=name,
            start_time=start_time,
            duration=duration,
            entry_type="measure",
            timestamp=timestamp,
        )
        return entry

    def clear_marks(self):
        self.data = [d for d in self.data if d["entryType"] != "mark"]

    def clear_measures(self):
        self.data = [d for d in self.data if d["entryType"] != "measure"]

    def clear(self):
        self.data = []

    def delete(self, name):
        self.data = [d for d in self.data if name not in d.name]

    def now(self):
        return time_in_millis(offset=get_offset(self))
