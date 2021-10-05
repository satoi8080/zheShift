import arrow
import auth as calendar

import config


def shift_list():
    service = calendar.main()
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
                'summary': event['summary'],
                'start': event['start'],
                'end': event['end']
            }
            service.events().insert(calendarId=config.export_calendar_ID, body=event_body).execute()
    return 0


if __name__ == '__main__':
    shift_list()
