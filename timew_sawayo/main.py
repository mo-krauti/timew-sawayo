import sys
import tomllib
from datetime import date
from os.path import expanduser, isfile
from typing import Union

from timewreport.interval import TimeWarriorInterval
from timewreport.parser import TimeWarriorParser

from timew_sawayo.ql_client_sawayo import QLClientSawayo
from timew_sawayo.utils import exit_with_msg

TIMEW_CONFIG_LOCATION = expanduser("~/.config/timewarrior/timewarrior.cfg")
DEFAULT_ENDPOINT = "https://work2.sawayo.de/graphql2/"
DEFAULT_TOKEN = "TOKEN"


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
    auto_token_firefox = timew_config.get("sawayo-sync-auto-token-firefox", False)

    ql_qlient_sawayo = QLClientSawayo(endpoint, token, auto_token_firefox)
    ql_qlient_sawayo._update_token_from_firefox()
    intervals: list[TimeWarriorInterval] = parser.get_intervals()
    previous_interval_date: Union[date, None] = None
    for interval in reversed(intervals):
        if interval.is_open():
            exit_with_msg(
                "Interval is not closed, stop tracking before syncing!", error=True
            )
        if interval.get_start_date() != interval.get_end_date():
            exit_with_msg(
                "Intervals spanning multiple dates not supported, you should not work during midnight!",  # noqa: long str
                error=True,
            )
        # only check if interval date changes
        if previous_interval_date != interval.get_start_date():
            if ql_qlient_sawayo.day_has_entries(interval.get_end_date()):
                exit_with_msg(
                    f"{interval.get_end_date().isoformat()} already has entries on sawayo, stopping sync"  # noqa: long str
                )
            else:
                previous_interval_date = interval.get_start_date()

        print(
            f"adding work entry from {interval.get_start().isoformat()} to {interval.get_end().isoformat()}"  # noqa: long str
        )
        ql_qlient_sawayo.ql_add_time_entry(
            "office", interval.get_start(), interval.get_end()
        )
