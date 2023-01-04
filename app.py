#!/usr/bin/python3

import os

from src.regexgen import generate_regex_for_ts, get_matches_from_file
from src.config import ProdConfig
from src.models import ValidatorLog


def crawl_log_files() -> None:
    directory = ProdConfig.PATH_VALIDATOR_LOG_FILES
    print(f"Crawling directory: {directory}")

    for r in ProdConfig.TIME_GAP_LIST:
        regex = generate_regex_for_ts(r[0], r[1])
        print(f"REGEX for range {r[0]} > {r[1]}:")
        print(f"{regex}")
        print(f"-"*50)

        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            print(f"Crawling file {filename}")

            if os.path.isfile(f):
                matches = get_matches_from_file(regex, f)
                ValidatorLog.load_list_matches(filename, matches)
                print(f"{len(matches)} matches found!")
    
    print("Done!")


if __name__ == "__main__":
    crawl_log_files()
