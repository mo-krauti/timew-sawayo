from typing import Union
from datetime import date
import sys
import tomllib
from os.path import isfile, expanduser


from timewreport.parser import TimeWarriorParser
from timewreport.interval import TimeWarriorInterval

from timew_sawayo.ql_client_sawayo import QLClientSawayo

TIMEW_CONFIG_LOCATION = expanduser("~/.config/timewarrior/timewarrior.cfg")
DEFAULT_ENDPOINT = "https://work2.sawayo.de/graphql2/"
DEFAULT_TOKEN = "TOKEN" 

def exit_with_msg(msg: str, error=False):
    print(msg)
    exit(error)

def load_timew_config() -> dict:
    if not isfile(TIMEW_CONFIG_LOCATION):
        exit_with_msg(f"create timew configuration at {TIMEW_CONFIG_LOCATION}")
    with open(TIMEW_CONFIG_LOCATION, "rb") as f:
        return tomllib.load(f)

def main():
    parser = TimeWarriorParser(sys.stdin)
    timew_config = load_timew_config()
    endpoint = timew_config.get("sawayo-sync-endpoint", DEFAULT_ENDPOINT)
    token = timew_config.get("sawayo-sync-token", DEFAULT_TOKEN)
    if token == DEFAULT_TOKEN:
        exit_with_msg("provide a sawayo token in the timew config", error=True)

    ql_qlient_sawayo = QLClientSawayo(endpoint, token)
    intervals: list[TimeWarriorInterval] = parser.get_intervals()
    previous_interval_date: Union[date, None] = None
    for interval in reversed(intervals):
        if interval.is_open():
            exit_with_msg("Interval is not closed, stop tracking before syncing!", error=True)
        if interval.get_start_date() != interval.get_end_date():
            exit_with_msg("Intervals spanning multiple dates not supported, you should not work during midnight!", error=True)
        # only check if interval date changes
        if previous_interval_date != interval.get_start_date():
            if ql_qlient_sawayo.day_has_entries(interval.get_end_date()):
                exit_with_msg(f"{interval.get_end_date().isoformat()} already has entries on sawayo, stopping sync")
            else:
                previous_interval_date = interval.get_start_date()

        print(f"adding work entry from {interval.get_start().isoformat()} to {interval.get_end().isoformat()}")
        input("say yes!")
        ql_qlient_sawayo.ql_add_time_entry("office", interval.get_start(), interval.get_end())
