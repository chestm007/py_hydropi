from py_hydropi.lib.threaded_daemon import ThreadedDaemon


class Switch(ThreadedDaemon):
    def __init__(self):
        super().__init__()
        self.attached_outputs = []
        self.outputs_activated = None

    @property
    def all_outputs(self):
        return list(self.attached_outputs)

    @classmethod
    def load_config(cls, raspberry_pi_timer, config):
        raise NotImplementedError

    def attach_object(self, obj):
        if type(obj) in (list, tuple):
            self.attached_outputs.extend(obj)
        else:
            self.attached_outputs.append(obj)
        return self

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

    def stop(self):
        super().stop()
        self._deactivate_objects()
