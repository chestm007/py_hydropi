from threading import Thread

from py_hydropi.lib.logger import Logger


class ThreadedDaemon:
    def __init__(self):
        self.logger = Logger(self.__class__.__name__)
        self._thread = None
        self._continue = False  # set to false to exit self._timer_loop

    def start(self):
        self._continue = True
        self._thread = Thread(target=self._main_loop)
        self._thread.start()
        return self

    def stop(self):
        self._continue = False

    def _main_loop(self):
        raise NotImplementedError

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
