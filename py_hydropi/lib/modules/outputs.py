from ..logger import Logger


class Output(object):
    logger = Logger('Output')

    def __init__(self, gpio, channel: int, initial_state=False):
        super().__init__()
        self.gpio = gpio
        self.channel = int(channel)
        self.state = initial_state
        self.gpio.setup_output_channel(self.channel, initial_state=initial_state)

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

    def toJSON(self):
        return {'channel': self.channel, 'state': self.state}
