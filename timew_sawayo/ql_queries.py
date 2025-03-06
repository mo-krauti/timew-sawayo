from gql import gql

QUERY_TIME_REPORT_DAY = gql(
    """
query TimeReportDay($input: TimeReportForDayInput!) {
  timeReportForDay(input: $input) {
    data {
      day
      workingDayStatus
      targetDuration
      actualDuration
      breakDuration
      closedTimeStatus
      dayEntries {
        ... on EmployeeTimeWeekReportDayTimeEntryDto {
          type
          startDateTime
          endDateTime
          duration
          entryType
          timeEntryId
          notes
          projectTags { _id
            backgroundColor
            color
            name
            __typename
          }
          __typename
        }
        ... on EmployeeTimeWeekReportDayPublicHolidayEntryDto {
          type
          startDateTime
          endDateTime
          duration
          occasion
          __typename
        }
        ... on EmployeeTimeWeekReportDayAbsenceEntryDto {
          absenceTemplateId
          type
          startDateTime
          endDateTime
          duration
          absenceTemplate {
            name
            __typename
          }
          __typename
        }
        ... on EmployeeTimeWeekReportDayAutomaticBreakDto {
          type
          duration
          __typename
        }
        __typename
      }
      __typename
    }
    error {
      unauthorized
      __typename
    }
    __typename
  }
}
"""
)

QUERY_ADD_TIME_ENTRY = gql(
"""
mutation AddTimeEntry($input: AddTimeEntryInput!) {
  addTimeEntry(input: $input) {
    data {
      _id
      __typename
    }
    error {
      closedTime
      unauthorized
      trackModeDisabled
      timePeriodDisabled
      overlappingAbsence
      futureEntryDisabled
      __typename
    }
    __typename
  }
}
"""
)
