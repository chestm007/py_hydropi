from ..logger import Logger


class Output(object):
    logger = Logger('Output')
    types = ('lights', 'water_pumps', 'air_pumps')

    def __init__(self, gpio, channel: int, initial_state=False, output_type=None):
        super().__init__()
        self.gpio = gpio
        self.channel = int(channel)
        self.state = initial_state
        self.gpio.setup_output_channel(self.channel, initial_state=initial_state)
        self.manual_control = False
        self.type = output_type

    def activate(self):
        """
        power the GPIO channel associated with this output
        """
        self.logger.info('activate signal recieved for channel {}. Signalling GPIO'.format(self.channel))
        self.state = True
        self.gpio.set_output_on(self.channel)

    def deactivate(self):
        """
        de-power the GPIO channel associated with this output
        """
        self.logger.info('deactivate signal recieved for channel {}. Signalling GPIO'.format(self.channel))
        self.state = False
        self.gpio.set_output_off(self.channel)

    def set_state(self, state):
        if state:
            self.activate()
        else:
            self.deactivate()

    def to_json(self):
        return {'channel': self.channel, 'state': self.state}
