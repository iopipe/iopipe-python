def add_timeline_measures(timeline):
    entries = timeline.get_entries_by_type('mark')
    names = [e.name for e in entries if e.name.startswith('start:') or e.name.startswith('end:')]
    for name in names:
        if name.startswith('start:'):
            _, base_name = name.split(':', 1)
            end_name = 'end:%s' % base_name
            if end_name in names:
                timeline.measure('measure:%s' % base_name, name, end_name)
