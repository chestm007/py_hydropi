from threading import Thread

from py_hydropi.lib.logger import Logger


class ThreadedDaemon:
    def __init__(self):
        self.logger = Logger(self.__class__.__name__)
        self._thread = None  # type: Thread
        self._continue = False  # set to false to exit self._timer_loop

    def start(self):
        self._continue = True
        self._thread = Thread(target=self._main_loop)
        self._thread.start()
        return self

    def stop(self):
        self.logger.info('recieved exit command, stopping terminating daemon main loop')
        self._continue = False
        if self._thread.is_alive():
            self._thread.join(timeout=self.frequency if hasattr(self, 'frequency') else 20)

    def _main_loop(self):
        raise NotImplementedError

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
