from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import arrow
import config

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    query = str(input("名前を入力（空欄で環境変数を読み取る）：") or config.myname)
    print('Getting the upcoming 40 events')
    events_result = service.events().list(calendarId=config.calendarId, timeMin=now,
                                          maxResults=40, singleEvents=True,
                                          orderBy='startTime',
                                          q=query).execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        start_time = arrow.get(start).format(fmt='HH:mm')
        start_date = arrow.get(start).format(fmt='YY年MM月DD日')
        start_day = arrow.get(start).format(fmt='DD日')
        shift = {'09:00': '早🔵', '12:00': '中🟣', '15:00': '遅🔴️'}
        # print(start, event['summary'])
        if start_time in shift:
            print(event['summary'], start_date, start_time, shift[start_time],start_day)
        else:
            print(event['summary'], start_date, start_time, '他⚪️',start_day)


if __name__ == '__main__':
    main()
