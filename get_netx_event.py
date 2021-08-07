import arrow
import datetime
import auth as calendar

import config


def tomorrow():
    service = calendar.main()
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    query = config.myname
    events_result = service.events().list(calendarId=config.calendar_ID, timeMin=now,
                                          maxResults=1, singleEvents=True,
                                          orderBy='startTime',
                                          q=query).execute()
    events = events_result.get('items', [])

    if not events:
        return 0
    else:
        event = events[0]
        shift = {'09:00': '早🔵', '12:00': '中🟣', '15:00': '遅🔴️'}
        start = event['start'].get('dateTime', event['start'].get('date'))
        start_time = arrow.get(start).format(fmt='HH:mm')
        event_shift = shift[start_time] if start_time in shift else '他⚪️'
        # print(start, event['summary'])
        return [event['summary'], start, event_shift]


if __name__ == '__main__':
    print(tomorrow())
