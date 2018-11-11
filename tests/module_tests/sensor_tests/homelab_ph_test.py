from module_tests.base_test_object import BaseTestObject
from py_hydropi.lib.modules.sensors.homelab_ph import HomeLabPH


class TestHomelabPH(BaseTestObject):
    @classmethod
    def setUpClass(cls):
        cls.homelabph = HomeLabPH(value_index='level')

    def set_ph(self, ph):
        self.homelabph.get_ph_command = 'echo \'{"level": "' + str(ph) + '"}\''

    def test_read(self):
        ph = 10
        self.set_ph(ph)
        self.homelabph._read()
        assert int(self.homelabph._value) == ph
