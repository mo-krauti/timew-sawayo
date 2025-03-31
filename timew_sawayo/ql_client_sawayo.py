from datetime import date, datetime

from browser_cookie3 import firefox
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport

from timew_sawayo.ql_queries import QUERY_ADD_TIME_ENTRY, QUERY_TIME_REPORT_DAY
from timew_sawayo.utils import check_optional_key_val_in_nested_dict, exit_with_msg


class QLClientSawayo:
    def __init__(self, endpoint: str, token: str, auto_token_firefox):
        self.endpoint = endpoint
        headers = {"x-sawayo-client-id": "employee-web-app"}
        self._transport = AIOHTTPTransport(url=endpoint, headers=headers, ssl=True)
        self._client = Client(
            transport=self._transport, fetch_schema_from_transport=False
        )
        self._set_token(token)
        self._auto_token_firefox = auto_token_firefox

    def _set_token(self, token: str):
        self._transport.cookies = {"active-access-token": token, "token": token}

    @staticmethod
    def _is_result_unauthorized(result) -> bool:
        for k, v in result.items():
            if check_optional_key_val_in_nested_dict(
                v, ["error", "unauthorized"], True
            ):
                return True
        return False

    def _update_token_from_firefox(self):
        if self._auto_token_firefox:
            token = ""
            print("trying to update token from firefox")
            for cookie in firefox(domain_name="sawayo.de"):
                if cookie.name == "token":
                    token = cookie.value
                    print("got token!")
            self._set_token(token)
        else:
            exit_with_msg(
                "auto updating token from firefox is disabled, update it manually"
            )

    def _execute(self, *args, try_updating_token=True, **kwargs):
        """
        execute wrapper catching auth errors
        """
        result = self._client.execute(*args, **kwargs)
        if self._is_result_unauthorized(result):
            print("auth token is invalid")
            if try_updating_token:
                self._update_token_from_firefox()
                result = self._execute(*args, try_updating_token=False, **kwargs)
            else:
                exit_with_msg(
                    "auth token is invalid, update it manually or login in browser"
                )
        return result

    def ql_time_report_day(self, day: date) -> dict:
        variables = {"input": {"forDay": day.isoformat(), "timeZone": "Europe_Berlin"}}
        return self._execute(
            QUERY_TIME_REPORT_DAY,
            operation_name="TimeReportDay",
            variable_values=variables,
        )

    def ql_add_time_entry(
        self, entry_type: str, start_datetime: datetime, end_datetime: datetime
    ) -> dict:
        if entry_type != "office" and entry_type != "break":
            raise ValueError("entry_type must be office or break")
        variables = {
            "input": {
                "endDateTime": end_datetime.isoformat(),
                "entryType": entry_type,
                "notes": "",
                "projectTagIds": [],
                "startDateTime": start_datetime.isoformat(),
            }
        }
        return self._execute(
            QUERY_ADD_TIME_ENTRY,
            operation_name="AddTimeEntry",
            variable_values=variables,
        )

    def day_has_entries(self, day: date) -> bool:
        time_report_day = self.ql_time_report_day(day)
        return len(time_report_day["timeReportForDay"]["data"]["dayEntries"]) > 0
