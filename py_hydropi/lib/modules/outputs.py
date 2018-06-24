from ..logger import Logger


class Output:
    types = ('lights', 'water_pumps', 'air_pumps')

    def __init__(self, gpio, channel: int, initial_state=False, output_type=None):
        self.logger = Logger(self.__class__.__name__)
        self.gpio = gpio
        self.channel = channel
        self.type = output_type
        self.state = initial_state
        self.gpio.setup_output_channel(self.channel, initial_state=initial_state)
        self.manual_control = False

    def activate(self):
        """
        power the GPIO channel associated with this output
        """
        if not self.state:
            self.logger.info('activate signal recieved for channel {}. Signalling GPIO'.format(self.channel))
            self.state = True
            self.gpio.set_output_on(self.channel)

    def deactivate(self):
        """
        de-power the GPIO channel associated with this output
        """
        if self.state:
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
