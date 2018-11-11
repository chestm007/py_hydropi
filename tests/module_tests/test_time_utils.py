from module_tests.base_test_object import BaseTestObject
from py_hydropi.lib import parse_clock_time_string, parse_simple_time_string


class TestTimeUtils(BaseTestObject):
    def test_parse_clock_time_string(self):
        on, off = parse_clock_time_string('3:00am - 4:00pm')
        self.assertEqual(on, '3:00am')
        self.assertEqual(off, '4:00pm')

    def test_parse_simple_time_string(self):
        for string in ('10s', '10m', '1h', '1h2m10s'):
            self.assertIsInstance(parse_simple_time_string(string), int)
