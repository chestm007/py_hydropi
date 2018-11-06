from py_hydropi.lib import parse_clock_time_string, parse_simple_time_string


class TestTimeUtils:
    def test_parse_clock_time_string(self):
        on, off = parse_clock_time_string('3:00am - 4:00pm')
        assert on == '3:00am'
        assert off == '4:00pm'

    def test_parse_simple_time_string(self):
        for string in ('10s', '10m', '1h', '1h2m10s'):
            assert type(parse_simple_time_string(string)) == int
