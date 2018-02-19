import time


def test_timeline(timeline):
    timeline.mark('start:foo')

    assert len(timeline.get_entries()) == 1
    assert len(timeline.get_entries_by_name('start:foo')) == 1
    assert len(timeline.get_entries_by_type('mark')) == 1
    assert len(timeline.get_entries_by_type('measure')) == 0

    timeline.mark('end:foo')

    assert len(timeline.get_entries()) == 2
    assert len(timeline.get_entries_by_name('end:foo')) == 1
    assert len(timeline.get_entries_by_type('mark')) == 2
    assert len(timeline.get_entries_by_type('measure')) == 0

    timeline.measure('foo', 'start:foo', 'end:foo')

    assert len(timeline.get_entries()) == 3
    assert len(timeline.get_entries_by_name('foo')) == 1
    assert len(timeline.get_entries_by_type('mark')) == 2
    assert len(timeline.get_entries_by_type('measure')) == 1

    start_foo = timeline.get_entries_by_name('start:foo')[0]
    end_foo = timeline.get_entries_by_name('end:foo')[0]
    measure_foo = timeline.get_entries_by_name('foo')[0]

    assert measure_foo.duration == end_foo.startTime - start_foo.startTime

    timeline.mark('start:bar')
    time.sleep(0.1)
    timeline.mark('end:bar')
    timeline.measure('bar', 'start:bar', 'end:bar')

    start_bar = timeline.get_entries_by_name('start:bar')[0]
    end_bar = timeline.get_entries_by_name('end:bar')[0]
    measure_bar = timeline.get_entries_by_name('bar')[0]

    assert 100.0 <= measure_bar.duration <= 150.0

    bar_duration = end_bar.startTime - start_bar.startTime
    assert bar_duration == measure_bar.duration
