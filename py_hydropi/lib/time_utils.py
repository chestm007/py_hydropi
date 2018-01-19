import re

SECONDS = 's'
MINUTES = 'm'
HOURS = 'h'
DAYS = 'd'


def parse_clock_time_string(string):
    on, off = string.split(' - ')
    return on, off


def parse_simple_time_string(string):
    total_mins = 0
    time_pattern = (
        '((?P<d>\d+){0})?((?P<h>\d+){1})?((?P<m>\d+){2})?((?P<s>\d+){3})?'.format(DAYS, HOURS, MINUTES, SECONDS))
    pattern = re.compile(time_pattern)

    found = pattern.search(string)
    if found:
        if found.group(SECONDS):
            total_mins += int(found.group(SECONDS)) / 60
        if found.group(MINUTES):
            total_mins += int(found.group(MINUTES))
        if found.group(HOURS):
            total_mins += int(found.group(HOURS)) * 60
        if found.group(DAYS):
            total_mins += int(found.group(DAYS)) * 24 * 60
    return total_mins
