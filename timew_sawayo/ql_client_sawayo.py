from datetime import datetime, date

from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport

from timew_sawayo.ql_queries import QUERY_TIME_REPORT_DAY, QUERY_ADD_TIME_ENTRY

class QLClientSawayo:
    def __init__(self, endpoint: str, token: str):
        headers = {"x-sawayo-client-id": "employee-web-app"}
        cookies = {
            "active-access-token": token,
            "token": token
        }

        self.transport = AIOHTTPTransport(url=endpoint, cookies=cookies, headers=headers, ssl=True)
        self.client = Client(transport=self.transport, fetch_schema_from_transport=False)

    def ql_time_report_day(self, day: date) -> dict:
        variables = {
            "input": {
                "forDay": day.isoformat(),
                "timeZone": "Europe_Berlin"
            }
        }
        return self.client.execute(QUERY_TIME_REPORT_DAY, operation_name="TimeReportDay", variable_values=variables)

    def ql_add_time_entry(self, entry_type: str, start_datetime: datetime, end_datetime: datetime) -> dict:
        if entry_type != "office" and entry_type != "break":
            raise ValueError("entry_type must be office or break")
        variables = {
            "input": {
                "endDateTime": end_datetime.isoformat(),
                "entryType": entry_type,
                "notes": "",
                "projectTagIds": [],
                "startDateTime": start_datetime.isoformat()
            }
        }
        return self.client.execute(QUERY_ADD_TIME_ENTRY, operation_name="AddTimeEntry", variable_values=variables)

    def day_has_entries(self, day: date) -> bool:
        time_report_day = self.ql_time_report_day(day)
        return len(time_report_day["timeReportForDay"]["data"]["dayEntries"]) > 0
