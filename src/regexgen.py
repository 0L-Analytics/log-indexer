#!/usr/bin/python3
import re

from typing import AnyStr, List

from .helpers import secs_between, print_range
from .config import ProdConfig, TestConfig


def generate_regex_for_ts(start_ts_string: AnyStr, end_ts_string: AnyStr) -> AnyStr:
    """
        Generate a (python re) regex to capture all timestamps between 
        2 given timestamps. Note that current version does not support
        interday capture as it cannot handle two dates withing the 
        range. Call the function multiple times for multiple dates.

        Given timestamp strings are not checked if they are valid!

        Format of both datestrings must be %Y-%m-%dT%H:%M:%S

        :param start_ts_string: start timestamp string
        :param end_ts_string: end timestamp string

        :return: regex for given timestamp range
    """
    # extract date part
    ds = start_ts_string[0:11:]
    de = end_ts_string[0:11:]

    if ds != de:
        # Script can only manage intraday ranges.
        print("DATES WITHIN A RANGE MUST BE EQUAL!!")
        raise Exception

    _H = (int(start_ts_string[11::12]), int(end_ts_string[11::12]))
    _h = (int(start_ts_string[12::13]), int(end_ts_string[12::13]))
    _M = (int(start_ts_string[14::15]), int(end_ts_string[14::15]))
    _m = (int(start_ts_string[15::16]), int(end_ts_string[15::16]))
    _S = (int(start_ts_string[17::18]), int(end_ts_string[17::18]))
    _s = (int(start_ts_string[18::19]), int(end_ts_string[18::19]))

    # countdown
    countdown = secs_between(start_ts_string, end_ts_string)
    # When will the next 10 sec roll over?  00:00:00 > 00:00:10
    next_roll = (10 - _s[0]) # (0-9)

    # DEBUG
    if ProdConfig.DEBUG == 1:
        print(f"############################# NEW ############################# {start_ts_string} > {end_ts_string}")
        print(f"[s] next_roll={next_roll} & countdown={countdown}")

    # Opening regex:
    str_out = "("

    if next_roll > countdown:
        str_out = f"{str_out}{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[0]}-{_s[1]}].*)"
        if ProdConfig.DEBUG == 1:
            print_range(str_out, start_ts_string, end_ts_string, tag=1, message="FINAL")
        return str_out
    elif next_roll == countdown:
        str_out = f"{str_out}{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]}][{_s[0]}-9].*"
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*)"
        if ProdConfig.DEBUG == 1:
            print_range(str_out, start_ts_string, end_ts_string, tag=2, message="FINAL")
        return str_out
    else:
        str_out = f"{str_out}{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]}][{_s[0]}{'' if _s[0]==9 else '-9'}].*"
        if ProdConfig.DEBUG == 1:
            print_range(str_out, start_ts_string, end_ts_string, tag=3, message="PARTIAL")

    countdown -= next_roll
    # When will the next 1 minute roll over?    00:00:00 > 00:01:00 
    next_roll = 60 - ((_S[0] + 1) *10) # (50-0)
    if ProdConfig.DEBUG == 1:
        print(f"[S] next_roll={next_roll} & countdown={countdown}")

    if next_roll == 0:
        # Do nothing... 
        # because this level rolls over with the previous regex
        ...
    elif countdown == 0:
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*)"
        if ProdConfig.DEBUG == 1:
            print_range(str_out, start_ts_string, end_ts_string, countdown, tag=4, message="FINAL")
        return str_out
    elif next_roll > countdown:
        if (_S[1] -(_S[0]+1)) == 0:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][0-{_s[1]}].*)"
            if ProdConfig.DEBUG == 1:
                print_range(str_out, start_ts_string, end_ts_string, countdown, tag=5, message="FINAL")
            return str_out
        elif (_S[1] -(_S[0]+1)) == 1:
            str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}][0-9].*"
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][0-{_s[1]}].*)"
            if ProdConfig.DEBUG == 1:
                print_range(str_out, start_ts_string, end_ts_string, countdown, tag=6, message="FINAL")
            return str_out
        else:
            str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}-{_S[1]-1}][0-9].*"
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
            if ProdConfig.DEBUG == 1:
                print_range(str_out, start_ts_string, end_ts_string, tag=7, message="FINAL")
            return str_out
    elif next_roll == countdown:
        str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}{'' if (_S[0]+1)==5 else '-5'}][0-9].*"
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*)"
        if ProdConfig.DEBUG == 1:
            print_range(str_out, start_ts_string, end_ts_string, tag=8, message="FINAL")
        return str_out
    else:
        str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}{'' if (_S[0]+1)==5 else '-5'}][0-9].*"
        if ProdConfig.DEBUG == 1:
            print_range(str_out, start_ts_string, end_ts_string, tag=9, message="PARTIAL")
        
    countdown -= next_roll
    # When will the next 10 minutes roll over?    00:00:00 > 00:10:00 
    next_roll = (10 - (_m[0]+1)) * 60
    if ProdConfig.DEBUG == 1:
        print(f"[m] next_roll={next_roll} & countdown={countdown}")

    if next_roll == 0:
        # Do nothing... 
        # because this level rolls over with the previous regex
        ...
    elif countdown == 0:
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*)"
        if ProdConfig.DEBUG == 1:
            print_range(str_out, start_ts_string, end_ts_string, countdown, tag=10, message="FINAL")
        return str_out
    elif next_roll > countdown:
        if countdown < 60:
            if _S[1] == 0:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[0][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
                if ProdConfig.DEBUG == 1:
                    print_range(str_out, start_ts_string, end_ts_string, countdown, tag=12, message="FINAL")
                return str_out
            else:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]==1 else f'0-{_S[1]-1}'}][0-9].*"
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
                if ProdConfig.DEBUG == 1:
                    print_range(str_out, start_ts_string, end_ts_string, countdown, tag=14, message="FINAL")
                return str_out
        else:
            # TODO: REWRITE THIS PART
            if _m[1] - (_m[0] + 1) == 1:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[0]+1}]\:[0-5][0-9].*"
                if _S[1] == 0:
                    str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[0][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
                    if ProdConfig.DEBUG == 1:
                        print_range(str_out, start_ts_string, end_ts_string, countdown, tag=15, message="FINAL")
                    return str_out
                else:
                    str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]==1 else (f'0-{_S[1]-1}')}][0-9].*"
                    str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
                    if ProdConfig.DEBUG == 1:
                        print_range(str_out, start_ts_string, end_ts_string, countdown, tag=16, message="FINAL")
                    return str_out
            else:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[0]+1}-{_m[1]-1}]\:[0-5][0-9].*"
                if _S[1] == 0:
                    str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
                    if ProdConfig.DEBUG == 1:
                        print_range(str_out, start_ts_string, end_ts_string, countdown, tag=17, message="FINAL")
                else:
                    str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]==1 else f'0-{_S[1]-1}'}][0-9].*"
                    str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
                    if ProdConfig.DEBUG == 1:
                        print_range(str_out, start_ts_string, end_ts_string, countdown, tag=18, message="FINAL")
                return str_out
    elif next_roll == countdown:
        str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]+1}{'' if (_m[0]+1)==9 else '-9'}]\:[0-5][0-9].*"
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*)"
        if ProdConfig.DEBUG == 1:
            print_range(str_out, start_ts_string, end_ts_string, tag=19, message="FINAL")
        return str_out
    else:
        str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]+1}{'' if (_m[0]+1)==9 else '-9'}]\:[0-5][0-9].*"
        if ProdConfig.DEBUG == 1:
            print_range(str_out, start_ts_string, end_ts_string, tag=20, message="PARTIAL")
        
        
    countdown -= next_roll
    # When will the next 1 hour roll over?    00:00:00 > 01:00:00 
    next_roll = (6 - (_M[0] + 1)) * 10 * 60
    if ProdConfig.DEBUG == 1:
        print(f"[M] next_roll={next_roll} & countdown={countdown}")

    if next_roll == 0:
        # Do nothing...
        ...
    elif countdown == 0:
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*)"
        if ProdConfig.DEBUG == 1:
            print_range(str_out, start_ts_string, end_ts_string, countdown, tag=21, message="FINAL")
        return str_out
    elif next_roll > countdown:
        if countdown <= 9:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
            if ProdConfig.DEBUG == 1:
                print_range(str_out, start_ts_string, end_ts_string, tag=22, message="FINAL")
            return str_out
        elif countdown < 60:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{f'0-{_S[1]-1}' if _S[1]>1 else '0'}][0-9].*"
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
            if ProdConfig.DEBUG == 1:
                print_range(str_out, start_ts_string, end_ts_string, tag=23, message="FINAL")
            return str_out
        elif countdown < 600:
            if _M[1] - (_M[0]+1) == 1:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]-1}][0-9]\:[0-5][0-9].*"
            elif _M[1] - (_M[0]+1) > 1:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[0]+1}-{_M[1]-1}][0-9]\:[0-5][0-9].*"
            
            if _m[1] >= 1:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{f'0-{_m[1]-1}' if _m[1]>1 else '0'}]\:[0-5][0-9].*"

            if _S[1] >= 1:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{f'0-{_S[1]-1}' if _S[1]>1 else '0'}][0-9].*"
            
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'0' if _s[1]==0 else f'0-{_s[1]}'}].*)"
            if ProdConfig.DEBUG == 1:
                print_range(str_out, start_ts_string, end_ts_string, tag=25, message="FINAL")
            return str_out 
        else:
            if _M[1] - (_M[0] + 1) == 1:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[0]+1}][0-9]\:[0-5][0-9].*"
            else:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[0]+1}-{_M[1]-1}][0-9]\:[0-5][0-9].*"

            if _m[1] > 0:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{'0' if _m[1]<=1 else f'0-{_m[1]-1}'}]\:[0-5][0-9].*"
            
            if _S[1] > 0:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]<=1 else f'0-{_S[1]-1}'}][0-9].*"

            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'0' if _s[1]==0 else f'0-{_s[1]}'}].*)"
            if ProdConfig.DEBUG == 1:
                print_range(str_out, start_ts_string, end_ts_string, tag=26, message="FINAL")
            return str_out
    else:
        str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{'5' if (_M[0]+1)==5 else f'{_M[0]+1}-5'}][0-9]\:[0-5][0-9].*"
        if ProdConfig.DEBUG == 1:
            print_range(str_out, start_ts_string, end_ts_string, tag=27, message="PARTIAL")

    countdown -= next_roll
    # When will the next 10 hour roll over?   00:00:00 > 10:00:00
    next_roll = (10 - (_h[0] + 1)) * 60 * 60    # (0-36000)
    if ProdConfig.DEBUG == 1:
        print(f"[h] next_roll={next_roll} & countdown={countdown}")

    if next_roll == 0:
        # Do nothing...
        ...
    elif countdown == 0:
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*)"
        if ProdConfig.DEBUG == 1:
            print_range(str_out, start_ts_string, end_ts_string, countdown, tag=28, message="FINAL")
        return str_out
    elif next_roll > countdown:
        if countdown <= 9:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
            if ProdConfig.DEBUG == 1:
                print_range(str_out, start_ts_string, end_ts_string, tag=29, message="FINAL")
            return str_out
        elif countdown < 60:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]<=1 else f'0-{_S[1]-1}'}][0-9].*"
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
            if ProdConfig.DEBUG == 1:
                print_range(str_out, start_ts_string, end_ts_string, tag=30, message="FINAL")
            return str_out
        elif countdown < 600:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{'0' if _m[1]==1 else f'0-{_m[1]-1}'}]\:[0-5][0-9].*"

            if _S[1] >= 1:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]==1 else f'0-{_S[1]-1}'}][0-9].*"

            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
            if ProdConfig.DEBUG == 1:
                print_range(str_out, start_ts_string, end_ts_string, tag=31, message="FINAL")
            return str_out
        elif countdown < 3600:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{'0' if _M[1]==1 else f'0-{_M[1]-1}'}][0-9]\:[0-5][0-9].*"

            if _m[1] > 0:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{'0' if _m[1]<=1 else f'0-{_m[1]-1}'}]\:[0-5][0-9].*"
            
            if _S[1] > 0:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]==1 else f'0-{_S[1]-1}'}][0-9].*"

            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'0' if _s[1]==0 else f'0-{_s[1]}'}].*)"
            if ProdConfig.DEBUG == 1:
                print_range(str_out, start_ts_string, end_ts_string, tag=32, message="FINAL")
            return str_out
        else:
            if _h[1] - (_h[0] + 1) == 1:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]+1}]\:[0-5][0-9]\:[0-5][0-9].*"
            else:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[0]+1}-{_h[1]-1}]\:[0-5][0-9]\:[0-5][0-9].*"

            if _M[1] > 0:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{'0' if _M[1]<=1 else f'0-{_M[1]-1}'}][0-9]\:[0-5][0-9].*"

            if _m[1] > 0:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{'0' if _m[1]<=1 else f'0-{_m[1]-1}'}]\:[0-5][0-9].*"
            
            if _S[1] > 0:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]==1 else f'0-{_S[1]-1}'}][0-9].*"

            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'0' if _s[1]==0 else f'0-{_s[1]}'}].*)"
            if ProdConfig.DEBUG == 1:
                print_range(str_out, start_ts_string, end_ts_string, tag=33, message="FINAL")
            return str_out
    else:
        str_out = f"{str_out}|{ds}[{_H[0]}][{'9' if (_M[0]+1)==9 else f'{_M[0]+1}-9'}]\:[0-5][0-9]\:[0-5][0-9].*"
        if ProdConfig.DEBUG == 1:
            print_range(str_out, start_ts_string, end_ts_string, tag=34, message="PARTIAL")   

    # update discounter
    countdown -= next_roll
    # When will the next day roll over?   00:00:00 > 10:00:00
    next_roll = (2 - (_H[0] + 1)) * 60 * 60 * 10

    if next_roll == 0:
        # TODO: Add code for dat range here...
        # This would be a new day...
        ...
    
    if countdown == 0:
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*)"
        if ProdConfig.DEBUG == 1:
            print_range(str_out, start_ts_string, end_ts_string, countdown, tag=35, message="FINAL")
        return str_out
    
    if countdown <= 9:
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
        if ProdConfig.DEBUG == 1:
            print_range(str_out, start_ts_string, end_ts_string, tag=36, message="FINAL")
        return str_out
    elif countdown < 60:
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]<=1 else f'0-{_S[1]-1}'}][0-9].*"
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
        if ProdConfig.DEBUG == 1:
            print_range(str_out, start_ts_string, end_ts_string, tag=37, message="FINAL")
        return str_out
    elif countdown < 600:
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{'0' if _m[1]==1 else f'0-{_m[1]-1}'}]\:[0-5][0-9].*"

        if _S[1] >= 1:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]==1 else f'0-{_S[1]-1}'}][0-9].*"

        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
        if ProdConfig.DEBUG == 1:
            print_range(str_out, start_ts_string, end_ts_string, tag=38, message="FINAL")
        return str_out
    elif countdown < 3600:
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{'0' if _M[1]==1 else f'0-{_M[1]-1}'}][0-9]\:[0-5][0-9].*"

        if _m[1] > 0:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{'0' if _m[1]<=1 else f'0-{_m[1]-1}'}]\:[0-5][0-9].*"
        
        if _S[1] > 0:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]==1 else f'0-{_S[1]-1}'}][0-9].*"

        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'0' if _s[1]==0 else f'0-{_s[1]}'}].*)"
        if ProdConfig.DEBUG == 1:
            print_range(str_out, start_ts_string, end_ts_string, tag=39, message="FINAL")
        return str_out
    else:
        if _H[1] - (_H[0]+1) == 1:
            str_out = f"{str_out}|{ds}[{_H[0]+1}][0-9]\:[0-5][0-9]\:[0-5][0-9].*"
        
        if _h[1] > 0:
            str_out = f"{str_out}|{ds}[{_H[1]}][{'0' if _h[1]<=1 else f'0-{_h[1]-1}'}]\:[0-5][0-9]\:[0-5][0-9].*"

        if _M[1] > 0:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{'0' if _M[1]<=1 else f'0-{_M[1]-1}'}][0-9]\:[0-5][0-9].*"

        if _m[1] > 0:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{'0' if _m[1]<=1 else f'0-{_m[1]-1}'}]\:[0-5][0-9].*"
        
        if _S[1] > 0:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]==1 else f'0-{_S[1]-1}'}][0-9].*"

        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'0' if _s[1]==0 else f'0-{_s[1]}'}].*)"
        if ProdConfig.DEBUG == 1:
            print_range(str_out, start_ts_string, end_ts_string, tag=40, message="FINAL")
        return str_out


def get_matches_from_file(
    regex_str: AnyStr,
    file_path: AnyStr = TestConfig.PATH_TEST_FILE) -> List:
    matches = []
    try:
        with open(file_path, "r") as f:
            filedata = f.read()
            matches = re.findall(regex_str, filedata)
    except Exception as e:
        print(f"regex_str={regex_str}")
        print(f"e={e}")
    return matches
