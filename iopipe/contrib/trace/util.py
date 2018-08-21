from iopipe.compat import binary_types


def add_timeline_measures(timeline):
    entries = timeline.get_entries_by_type("mark")
    measures = timeline.get_entries_by_type("measure")
    entry_names = [
        e.name
        for e in entries
        if e.name.startswith("start:") or e.name.startswith("end:")
    ]
    measure_names = [m.name for m in measures]
    for name in entry_names:
        if name.startswith("start:"):
            _, base_name = name.split(":", 1)
            end_name = "end:%s" % base_name
            measure_name = "measure:%s" % base_name
            if end_name in entry_names and measure_name not in measure_names:
                timeline.measure(measure_name, name, end_name)


def ensure_utf8(v):
    """Ensures that a binary value is decoded into utf-8"""
    if isinstance(v, binary_types):
        return v.decode("utf-8", "ignore")
    return v
