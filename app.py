import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import config
import arrow

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
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


def shift_list_print():
    service = main()
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    # query = str(input("名前を入力（空欄で環境変数を読み取る）：") or config.myname)
    query = config.myname
    results_length = 100
    print('Getting the upcoming at most ' + str(results_length) + ' events')
    events_result = service.events().list(calendarId=config.read_calendar_ID, timeMin=now,
                                          maxResults=results_length, singleEvents=True,
                                          orderBy='startTime',
                                          q=query).execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        start_time = arrow.get(start).format(fmt='HH:mm')
        start_date = arrow.get(start).format(fmt='MM月YY年')
        start_day = arrow.get(start).format(fmt='DD日')
        shift = {'09:00': '早🔵', '12:00': '中🟣', '15:00': '遅🔴️'}
        event_shift = shift[start_time] if start_time in shift else '他⚪️'
        # print(start, event['summary'])
        print(event['summary'], start_time, event_shift, start_day, start_date)


def shift_list_export():
    service = main()
    arrow_now = arrow.now(tz=config.timezone)
    next_month_start_utc = arrow_now.shift(months=1).replace(day=1, hour=0, minute=0, second=0, microsecond=0).to('UTC')
    # Beginning of Next Month
    next_month_start_utc_iso = next_month_start_utc.datetime.isoformat()
    # Beginning of the Month after Next
    next_month_end_utc = arrow_now.shift(months=2).replace(day=1, hour=0, minute=0, second=0, microsecond=0).to('UTC')
    next_month_end_utc_iso = next_month_end_utc.datetime.isoformat()

    # query = str(input("名前を入力（空欄で環境変数を読み取る）：") or config.myname)
    query = config.myname
    results_length = 100
    print('Getting the upcoming at most ' + str(results_length) + ' events')
    events_result = service.events().list(calendarId=config.read_calendar_ID,
                                          timeMin=next_month_start_utc_iso,
                                          timeMax=next_month_end_utc_iso,
                                          maxResults=results_length, singleEvents=True,
                                          orderBy='startTime',
                                          q=query).execute()
    events = events_result.get('items', [])
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        start_time = arrow.get(start).format(fmt='HH:mm')
        start_date = arrow.get(start).format(fmt='MM月YY年')
        start_day = arrow.get(start).format(fmt='DD日')
        shift = {'09:00': '早🔵', '12:00': '中🟣', '15:00': '遅🔴️'}
        event_shift = shift[start_time] if start_time in shift else '他⚪️'
        # print(start, event['summary'])
        print(event['summary'], start_time, event_shift, start_day, start_date)
        if event['summary']:
            event_body = {
                'summary': event['summary'] + shift,
                'start': event['start'],
                'end': event['end']
            }
            service.events().insert(calendarId=config.export_calendar_ID, body=event_body).execute()
    return 0



if __name__ == '__main__':
    main()
