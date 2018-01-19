class Output(object):
    def __init__(self, gpio, channel, initial_state=False):
        super().__init__()
        self.gpio = gpio
        self.channel = channel
        self.state = initial_state
        self.gpio.setup_output_channel(self.channel, initial_state=initial_state)

    def activate(self):
        """
        power the GPIO channel associated with this output
        """
        self.gpio.set_output_on(self.channel)

    def deactivate(self):
        """
        de-power the GPIO channel associated with this output
        """
        self.gpio.set_output_off(self.channel)