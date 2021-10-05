import arrow
import datetime
import auth as calendar

import config


def shift_list():
    service = calendar.main()
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


if __name__ == '__main__':
    shift_list()
