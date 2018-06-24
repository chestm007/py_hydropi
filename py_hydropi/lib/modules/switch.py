from threading import Thread

from py_hydropi.lib.logger import Logger


class Switch:
    def __init__(self):
        self.logger = Logger(self.__class__.__name__)
        self.attached_outputs = []
        self._thread = None
        self._continue = True  # set to false to exit self._timer_loop
        self.outputs_activated = False

    def attach_object(self, obj):
        self.attached_outputs.append(obj)

    def _activate_objects(self):
        if not self.outputs_activated:
            for output in self.attached_outputs:
                if output.manual_control:
                    self.logger.info('output {} is manually controlled, skipping signal'.format(output.channel))
                else:
                    self.logger.info('signalling output {} to activate'.format(output.channel))
                    output.activate()
            self.outputs_activated = True

    def _deactivate_objects(self):
        if self.outputs_activated:
            for output in self.attached_outputs:
                if output.manual_control:
                    self.logger.info('output {} is manually controlled, skipping signal'.format(output.channel))
                else:
                    self.logger.info('signalling output {} to deactivate'.format(output.channel))
                    output.deactivate()
            self.outputs_activated = False

    def start(self):
        self._thread = Thread(target=self._main_loop)
        self._thread.start()

    def stop(self):
        self._deactivate_objects()
        self._continue = False

    def _main_loop(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


