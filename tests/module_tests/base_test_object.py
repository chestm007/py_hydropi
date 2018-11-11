from py_hydropi.lib import Output
from py_hydropi.lib.modules.inputs import Input
import unittest


class BaseTestObject(unittest.TestCase):
    class MockOutput(Output):
        def __init__(self, channel):
            self.channel = channel
            self.active = False
            self.manual_control = False
            self.state = False

        def activate(self):
            self.active = True
            print('activate {}'.format(self.channel))

        def deactivate(self):
            self.active = False
            print('deacivate {}'.format(self.channel))

    class MockInput(Input):
        value = 0

        def __init__(self):
            self.falling = True
