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
