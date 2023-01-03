#!/usr/bin/python3

import re

from typing import AnyStr, List
from datetime import datetime, timedelta

from src.helpers import secs_between
from src.regexgen import generate_regex_for_ts
from src.config import Config

# time gaps
time_gap_list = [
    ("2022-11-21T23:00:00", "2022-11-22T01:55:00"),
]


def run_test(
    regex_str: AnyStr,
    file_path: AnyStr = Config.PATH_TEST_FILE) -> List:
    matches = []
    try:
        with open(file_path, "r") as f:
            filedata = f.read()
            matches = re.findall(regex_str, filedata)
    except Exception as e:
        print(f"regex_str={regex_str}")
        print(f"e={e}")
    return matches


def main():
    break_flag = False
    start_ts_str = "2022-01-01T00:00:00"
    start_ts = datetime.strptime(start_ts_str, '%Y-%m-%dT%H:%M:%S')
    end_ts_str = "2022-01-01T21:00:01"
    end_ts = datetime.strptime(end_ts_str, '%Y-%m-%dT%H:%M:%S')

    total_seconds = secs_between(start_ts_str, end_ts_str)

    for i in range(0, total_seconds+1):
        subj_start_ts = start_ts + timedelta(seconds=i)
        subj_start_str = datetime.strftime(subj_start_ts, '%Y-%m-%dT%H:%M:%S')
        for j in range(0, total_seconds-i):
            subj_end_ts = end_ts - timedelta(seconds=j)
            subj_end_str = datetime.strftime(subj_end_ts, '%Y-%m-%dT%H:%M:%S')

            regex = generate_regex_for_ts(subj_start_str, subj_end_str)
            matches = run_test(regex)
            expectation = secs_between(subj_start_str, subj_end_str) +1
            if len(matches) != expectation:
                print("__________________________________________________ERROR__________________________________________________")
                print(f"[Result does not match!] {subj_start_str} > {subj_end_str}")
                print(regex)
                # print(f"matches={matches}")
                break_flag = True
                break
        if break_flag:
            break


if __name__ == "__main__":
    main()
