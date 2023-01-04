#!/usr/bin/python3

from datetime import datetime, timedelta
from typing import AnyStr

from src.helpers import secs_between
from src.regexgen import generate_regex_for_ts, get_matches_from_file
from src.config import TestConfig

if TestConfig.SOUND_ON_ERROR == 1:
    import os


def test_ts_time_range(start_ts_str: AnyStr, end_ts_str: AnyStr):
    break_flag = False
    start_ts = datetime.strptime(start_ts_str, '%Y-%m-%dT%H:%M:%S')
    end_ts = datetime.strptime(end_ts_str, '%Y-%m-%dT%H:%M:%S')
    total_seconds = secs_between(start_ts_str, end_ts_str)

    for i in range(0, total_seconds+1):
        subj_start_ts = start_ts + timedelta(seconds=i)
        subj_start_str = datetime.strftime(subj_start_ts, '%Y-%m-%dT%H:%M:%S')
        for j in range(0, total_seconds-i):
            subj_end_ts = end_ts - timedelta(seconds=j)
            subj_end_str = datetime.strftime(subj_end_ts, '%Y-%m-%dT%H:%M:%S')

            regex = generate_regex_for_ts(subj_start_str, subj_end_str)
            matches = get_matches_from_file(regex)
            expectation = secs_between(subj_start_str, subj_end_str) +1
            if len(matches) != expectation:
                print("__________________________________________________ERROR__________________________________________________")
                print(f"[Result does not match!] {subj_start_str} > {subj_end_str}")
                print(regex)
                # print(f"matches={matches}")
                break_flag = True

                if TestConfig.SOUND_ON_ERROR == 1:
                    # Make a sound in Linux!:
                    os.system("aplay -d 1 ./assets/sin.wav")
                break
        if break_flag:
            break
