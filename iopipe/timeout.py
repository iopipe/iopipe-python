import ctypes
import signal
import sys
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


class SignalTimeout(object):
    def __init__(self, seconds):
        self.seconds = seconds

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.stop)
        if self.seconds > 0:
            signal.setitimer(signal.ITIMER_REAL, self.seconds)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cancel()
        return False

    def cancel(self):
        signal.setitimer(signal.ITIMER_REAL, 0)

    def stop(self, signum, frame):
        raise TimeoutError


class ThreadTimeout(object):
    def __init__(self, seconds):
        self.seconds = seconds
        self.target_tid = threading.current_thread().ident
        self.timer = None

    def __enter__(self):
        self.timer = threading.Timer(self.seconds, self.stop)
        if self.seconds > 0:
            self.timer.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cancel()
        return False

    def cancel(self):
        if self.timer:
            self.timer.cancel()

    def stop(self):
        async_raise(self.target_tid, TimeoutError)


class TimeoutError(Exception):
    def __init__(self, *args, **kwargs):
        default_message = "Timeout Exceeded."
        if not (args or kwargs):
            args = (default_message,)
        super(TimeoutError, self).__init__(*args, **kwargs)


if sys.platform == "win32":
    Timeout = ThreadTimeout
else:
    Timeout = SignalTimeout
