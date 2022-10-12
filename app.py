import os.path
import webbrowser
from datetime import timedelta
from distutils.util import strtobool
import rich.table
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
# ------------------------------------------------
import config
import arrow
from rich import print

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
    print('From: ', month_start_utc.format('YYYY-MM-DD HH:mm:ss'), 'UTC')
    month_start_utc_iso = month_start_utc.datetime.isoformat()

    month_end_utc = arrow_now.shift(months=month_offset + 1).replace(day=1, hour=0, minute=0, second=0,
                                                                     microsecond=0).to('UTC')
    print('To:   ', month_end_utc.format('YYYY-MM-DD HH:mm:ss'), 'UTC')
    # Beginning of the Month after Next
    month_end_utc_iso = month_end_utc.datetime.isoformat()

    # query = str(input("Input event title keyword：") or config.myname)
    query = config.query_name

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

            shift = {'09:00': '早🟦', '12:00': '中🟪', '15:00': '遅🟥'}
            if config.EIGHT_HOUR_SHIFT:
                shift = {'09:00': '早🟦', '12:00': '遅🟥'}

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

    def count_late_sunday_and_holiday_and_error_check():
        count_total_shift = 0
        count_early_shift = 0
        count_mid_shift = 0
        count_late_shift = 0
        count_non_sun_nor_holiday_shift = 0
        count_sun_or_holiday_shift = 0
        print('Getting the ' + str(max_results) + ' events for stat and error check')

        events_result = service.events().list(calendarId=config.import_calendar_ID,
                                              timeMin=month_start_utc_iso,
                                              timeMax=month_end_utc_iso,
                                              maxResults=max_results, singleEvents=True,
                                              orderBy='startTime',
                                              q=query
                                              ).execute()

        holiday_result = service.events().list(calendarId='ja.japanese.official#holiday@group.v.calendar.google.com',
                                               timeMin=month_start_utc_iso,
                                               timeMax=month_end_utc_iso,
                                               maxResults=max_results, singleEvents=True,
                                               orderBy='startTime',
                                               ).execute()

        events = events_result.get('items', [])
        holidays = holiday_result.get('items', [])

        if not events:
            print('No upcoming Events found.')
        if not holidays:
            print('No upcoming Holidays found.')

        holidays_date_list = []

        for holiday in holidays:
            holiday_start = holiday['start'].get('dateTime', holiday['start'].get('date'))
            holiday_start_date = arrow.get(holiday_start).format(fmt='YYYYMMDD')
            holidays_date_list.append(holiday_start_date)

        for event_index in range(len(events)):
            event = events[event_index]
            next_event = events[event_index + 1] if event_index + 1 < len(events) else None

            event_start = event['start'].get('dateTime', event['start'].get('date'))
            next_event_start = next_event['start'].get('dateTime',
                                                       next_event['start'].get('date')) if next_event else None
            event_start_date_str = arrow.get(event_start).format(fmt='YYYYMMDD')
            event_start_date_obj = arrow.get(event_start).date()
            next_event_start_date_str = arrow.get(next_event_start).format(fmt='YYYYMMDD') if next_event_start else None
            next_event_start_date_obj = arrow.get(next_event_start).date() if next_event_start else None
            event_start_time = arrow.get(event_start).format(fmt='HH:mm')
            next_event_start_time = arrow.get(next_event_start).format(fmt='HH:mm') if next_event_start else None
            event_start_weekday = arrow.get(event_start).isoweekday() if next_event_start else None
            next_event_start_weekday = arrow.get(next_event_start).isoweekday() if next_event_start else None

            if event_start_time == config.LATE_START_TIME and next_event_start_time == config.EARLY_START_TIME:
                if next_event_start_date_obj == event_start_date_obj + timedelta(days=1):
                    print('遅早 found between ' + event_start_date_str + ' and ' + next_event_start_date_str)

            # isoweekday() Monday is 1 and Sunday is 7
            count_total_shift += 1

            if event_start_time == config.EARLY_START_TIME:
                count_early_shift += 1
            if event_start_time == config.MID_START_TIME:
                count_mid_shift += 1
            if event_start_time == config.LATE_START_TIME:
                count_late_shift += 1

            is_late = event_start_time == config.LATE_START_TIME
            is_weekday_or_sat = (event_start_weekday != 7) and (event_start_date_str not in holidays_date_list)
            is_sunday_or_holiday = (event_start_weekday == 7) or (event_start_date_str in holidays_date_list)
            # Duplicates !is_weekday_or_sat though, for convenience of future change
            if is_late and is_weekday_or_sat:
                count_non_sun_nor_holiday_shift += 1
            if is_sunday_or_holiday:
                print('Sunday or holiday found: ' + event_start_date_str)
                count_sun_or_holiday_shift += 1
        table = rich.table.Table(title='Shift Summary')
        table.add_column('Type')
        table.add_column('Count')
        table.add_row('EARLY', str(count_early_shift))
        table.add_row('MID (Late for 8 hour)', str(count_mid_shift))
        table.add_row('LATE', str(count_late_shift))
        table.add_row('Monday ~ Saturday Late', str(count_non_sun_nor_holiday_shift))
        table.add_row('Sunday or Holiday All', str(count_sun_or_holiday_shift))
        return print('\n',
                     table
                     )

    if clear_old_export:
        do_clear_old_export()
    if add_new_export:
        do_add_new_export()
    count_late_sunday_and_holiday_and_error_check()

    return 0


if __name__ == '__main__':
    auth()
    get_shift_list(
        clear_old_export=bool(strtobool(input('Clear Events? 1 for True or 0 for false: <default: 1> ') or '1')),
        add_new_export=bool(strtobool(input('Add New Events? 1 for True or 0 for false: <default: 1> ') or '1')),
        month_offset=int(input('Month offset like -1, 0, 1: <default: 1> ') or '1')
    )
    webbrowser.open_new_tab(config.export_calendar_URL)
