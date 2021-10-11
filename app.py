import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import config
import arrow

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def auth():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    # # Call the Calendar API
    # now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    # print('Getting the upcoming 10 events')
    # events_result = service.events().list(calendarId='primary', timeMin=now,
    #                                       maxResults=10, singleEvents=True,
    #                                       orderBy='startTime').execute()
    # events = events_result.get('items', [])
    #
    # if not events:
    #     print('No upcoming events found.')
    # for event in events:
    #     start = event['start'].get('dateTime', event['start'].get('date'))
    #     print(start, event['summary'])

    return service


def get_shift_list(clear_old_export: bool = True,
                   add_new_export: bool = True,
                   month_offset: int = 1,
                   max_results: int = 100):
    """

    :param clear_old_export: If True, old export events will be cleaered
    :param add_new_export: If True, new exportable events will be exported
    :param month_offset: Normally 1 for next month, 0 for this month, -1 for last month
    :param max_results: Max events to export, normally no more than 31 I think, but still set default to 100
    :return: If no error, returns 0
    """
    service = auth()

    arrow_now = arrow.now(tz=config.timezone)

    month_start_utc = arrow_now.shift(months=month_offset).replace(day=1, hour=0, minute=0, second=0,
                                                                   microsecond=0).to('UTC')
    # Beginning of Next Month
    month_start_utc_iso = month_start_utc.datetime.isoformat()

    month_end_utc = arrow_now.shift(months=month_offset + 1).replace(day=1, hour=0, minute=0, second=0,
                                                                     microsecond=0).to('UTC')

    # Beginning of the Month after Next
    month_end_utc_iso = month_end_utc.datetime.isoformat()

    # query = str(input("Input event title keyword：") or config.myname)
    query = config.queryname

    def do_clear_old_export():
        if clear_old_export:
            print('Getting the old exported ' + str(max_results) + ' events')
            old_events_result = service.events().list(calendarId=config.export_calendar_ID,
                                                      timeMin=month_start_utc_iso,
                                                      timeMax=month_end_utc_iso,
                                                      maxResults=max_results, singleEvents=True,
                                                      orderBy='startTime',
                                                      q=query).execute()
            old_events = old_events_result.get('items', [])
            if not old_events:
                print('No events found.')
            for old_event in old_events:
                service.events().delete(calendarId=config.export_calendar_ID, eventId=old_event['id']).execute()
                print('Deleted old event ' + old_event['summary'])
        return 0

    def do_add_new_export():
        print('Getting the ' + str(max_results) + ' events to import')
        events_result = service.events().list(calendarId=config.import_calendar_ID,
                                              timeMin=month_start_utc_iso,
                                              timeMax=month_end_utc_iso,
                                              maxResults=max_results, singleEvents=True,
                                              orderBy='startTime',
                                              q=query).execute()
        events = events_result.get('items', [])
        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))

            start_time = arrow.get(start).format(fmt='HH:mm')
            start_date = arrow.get(start).format(fmt='DD日MM月YY年')

            shift = {'09:00': '早🔵', '12:00': '中🟣', '15:00': '遅🔴️'}

            event_shift = shift[start_time] if start_time in shift else '他⚪️'
            event_details = event['summary'] + start_time + event_shift + start_date
            print('Read: ' + event_details)

            if add_new_export:
                event_body = {
                    'summary': event['summary'] + ' - ' + event_shift,
                    'start': event['start'],
                    'end': event['end']
                }
                service.events().insert(calendarId=config.export_calendar_ID, body=event_body).execute()
                print('Exported: ' + event_details)
        return 0

    def count_late_sunday_and_holiday():
        count_late_shift = 0
        count_sunday_shift = 0
        count_holiday_non_late_shift = 0
        print('Getting the ' + str(max_results) + ' events to import')
        events_result = service.events().list(calendarId=config.import_calendar_ID,
                                              timeMin=month_start_utc_iso,
                                              timeMax=month_end_utc_iso,
                                              maxResults=max_results, singleEvents=True,
                                              orderBy='startTime',
                                              q=query).execute()
        holiday_result = service.events().list(calendarId='ja.japanese.official#holiday@group.v.calendar.google.com',
                                               timeMin=month_start_utc_iso,
                                               timeMax=month_end_utc_iso,
                                               maxResults=max_results, singleEvents=True,
                                               orderBy='startTime', ).execute()
        events = events_result.get('items', [])
        holidays = holiday_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        if not holidays:
            print('No upcoming holidays found.')

        holidays_date_list = []

        for holiday in holidays:
            holiday_start = holiday['start'].get('dateTime', holiday['start'].get('date'))
            holliday_start_date = arrow.get(holiday_start).format(fmt='YYYYMMDD')
            holidays_date_list.append(holliday_start_date)

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start_date = arrow.get(start).format(fmt='YYYYMMDD')
            start_time = arrow.get(start).format(fmt='HH:mm')
            start_weekday = arrow.get(start).isoweekday()
            # isoweekday() Monday is 1 and Sunday is 7

            if start_time == '15:00':
                count_late_shift += 1
            if start_weekday == 7 and start_time != '15:00':
                count_sunday_shift += 1
            if start_date in holidays_date_list and start_time != '15:00':
                count_holiday_non_late_shift += 1

        return {'Late_shift': count_late_shift,
                'Sunday_shift': count_sunday_shift,
                'Holiday_shift': count_holiday_non_late_shift}

    if clear_old_export:
        do_clear_old_export()
    if add_new_export:
        do_add_new_export()
    count_late_sunday_and_holiday()

    return 0


if __name__ == '__main__':
    auth()
    get_shift_list(clear_old_export=False,
                   add_new_export=False,
                   month_offset=1)
