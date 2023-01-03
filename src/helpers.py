from datetime import datetime, timedelta
from typing import AnyStr


def secs_between(start_ts_string: AnyStr, end_ts_string: AnyStr) -> int:
    a = datetime.strptime(start_ts_string, "%Y-%m-%dT%H:%M:%S")
    b = datetime.strptime(end_ts_string, "%Y-%m-%dT%H:%M:%S")
    return int((b-a).total_seconds())


def print_range(regex, start, end, seconds_rest=None, tag="", message=""):
    if seconds_rest:
        secs_between_start_end = secs_between(start, end)
        seconds_from_start = secs_between_start_end - seconds_rest
        new_start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S") + timedelta(seconds=seconds_from_start)
        start = datetime.strftime(new_start, "%Y-%m-%dT%H:%M:%S")
    print(f"<{tag}>[{message}]={regex}")
