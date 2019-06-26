def test_default_iopipe(default_iopipe):
    """Asserts that the default agent comes preloaded"""
    iopipe = default_iopipe

    assert len(iopipe.plugins) == 3
    assert iopipe.plugins[0].name == "trace"
    assert iopipe.plugins[1].name == "event-info"
    assert iopipe.plugins[2].name == "profiler"


def test_default_iopipe_override(default_iopipe_override):
    """Asserts the default agent can be overridden"""
    iopipe = default_iopipe_override

    assert len(iopipe.plugins) == 3
    assert iopipe.plugins[0].name == "event-info"
    assert iopipe.plugins[1].name == "profiler"
    assert iopipe.plugins[2].name == "trace"

    assert iopipe.plugins[2].auto_measure is False
