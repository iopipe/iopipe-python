import ctypes
import threading


def async_raise(target_tid, exception):
    # Ensuring and releasing GIL are useless since we're not in C
    # gil_state = ctypes.pythonapi.PyGILState_Ensure()
    ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(target_tid), ctypes.py_object(exception)
    )
    # ctypes.pythonapi.PyGILState_Release(gil_state)
    if ret == 0:
        raise ValueError("Invalid thread ID %s" % target_tid)
    elif ret > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(target_tid), None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class Timeout(object):
    EXECUTED, EXECUTING, TIMED_OUT, INTERRUPTED, CANCELED = range(5)

    def __init__(self, seconds, swallow_exc=True):
        self.seconds = seconds
        self.swallow_exc = swallow_exc
        self.state = Timeout.EXECUTED
        self.target_tid = threading.current_thread().ident
        self.timer = None

    def __bool__(self):
        return self.state in (Timeout.EXECUTED, Timeout.EXECUTING, Timeout.CANCELED)

    __nonzero__ = __bool__

    def __repr__(self):
        return "<{0} in state: {1}>".format(self.__class__.__name__, self.state)

    def __enter__(self):
        self.state = Timeout.EXECUTING
        self.setup_interrupt()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is TimeoutError:
            if self.state != Timeout.TIMED_OUT:
                self.state = Timeout.INTERRUPTED
                self.suppress_interrupt()
            return self.swallow_exc
        else:
            if exc_type is None:
                self.state = Timeout.EXECUTED
            self.suppress_interrupt()
        return False

    def cancel(self):
        self.state = Timeout.CANCELED
        self.suppress_interrupt()

    def stop(self):
        self.state = Timeout.TIMED_OUT
        async_raise(self.target_tid, TimeoutError)

    def setup_interrupt(self):
        self.timer = threading.Timer(self.seconds, self.stop)
        if self.seconds > 0:
            self.timer.start()

    def suppress_interrupt(self):
        self.timer.cancel()


class TimeoutError(Exception):
    def __init__(self, *args, **kwargs):
        default_message = "Timeout Exceeded."
        if not (args or kwargs):
            args = (default_message,)
        super(TimeoutError, self).__init__(*args, **kwargs)
