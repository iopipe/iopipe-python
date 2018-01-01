def test_marker__measure_no_start_or_end(marker):
    marker.start('foobar')
    marker.end('foobar')
    marker.measure('foobar')

    assert len(marker.timeline.get_entries()) == 3
    assert any([e.name == 'measure:foobar' for e in marker.timeline.get_entries()])


def test_marker__measure_start_only(marker):
    marker.start('foobar')
    marker.end('foobar')
    marker.end('barbaz')
    marker.measure('barbaz', 'foobar')

    assert len(marker.timeline.get_entries()) == 4
    assert any([e.name == 'measure:barbaz' for e in marker.timeline.get_entries()])


def test_marker__measure_different_start_and_end(marker):
    marker.start('foobar')
    marker.end('barbaz')
    marker.measure('barbaz', 'foobar', 'barbaz')

    assert len(marker.timeline.get_entries()) == 3
    assert any([e.name == 'measure:barbaz' for e in marker.timeline.get_entries()])


def test_marker__measure_no_marks(marker):
    marker.measure('foobar')

    assert len(marker.timeline.get_entries()) == 1
    assert any([e.name == 'measure:foobar' for e in marker.timeline.get_entries()])


def test_marker__context_manager(marker):
    with marker('foobar'):
        pass

    assert len(marker.timeline.get_entries()) == 2


def test_marker__nested_context_manager(marker):
    with marker('foobar') as nested_marker:
        with nested_marker('barbaz'):
            pass

    assert len(marker.timeline.get_entries()) == 4
