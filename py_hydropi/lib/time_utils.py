import re
from datetime import datetime

SECONDS = 's'
MINUTES = 'm'
HOURS = 'h'
DAYS = 'd'


def parse_clock_time_string(string):
    on, off = string.split(' - ')
    return on, off


def parse_simple_time_string(string):
    total_secs = 0
    time_pattern = (
        '((?P<d>\d+){0})?((?P<h>\d+){1})?((?P<m>\d+){2})?((?P<s>\d+){3})?'.format(DAYS, HOURS, MINUTES, SECONDS))
    pattern = re.compile(time_pattern)

    found = pattern.search(string)
    if found:
        if found.group(SECONDS):
            total_secs += int(found.group(SECONDS))
        if found.group(MINUTES):
            total_secs += int(found.group(MINUTES)) * 60
        if found.group(HOURS):
            total_secs += int(found.group(HOURS)) * 60 * 60
        if found.group(DAYS):
            total_secs += int(found.group(DAYS)) * 24 * 60 * 60
    return total_secs


def time_to_datetime(now, time):
    time_string = now.strftime('%b %d %Y {}'.format(time))
    return datetime.strptime(time_string, '%b %d %Y %I:%M%p')
