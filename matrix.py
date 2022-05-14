from typing import Tuple

import arrow
import pandas as pd
from arrow import Arrow


def get_natural_monthly_date_span(year: int, month: int) -> list:
    # Get the first day of the month
    start_date = arrow.get(f'{year}-{month}-01')
    # Get the last day of the month
    end_date = start_date.shift(months=1).shift(days=-1)
    # Get the date span range by day
    date_span = arrow.Arrow.range('day', start_date.datetime, end_date.datetime)
    # Convert the date span to a list of date strings in YYYY-MM-DD
    date_list = [date.format('YYYY-MM-DD') for date in date_span]
    return date_list


# isoweekdays() returns 1~7, where 1 is Monday and 7 is Sunday

def get_true_monthly_date_span(year: int, month: int, start_of_week_iso: int) -> list:
    begin_of_the_month = arrow.get(f'{year}-{month}-01')
    end_of_the_month = begin_of_the_month.shift(months=1).shift(days=-1)
    # Get the date span range extended days according to the beginning of week given
    # With the beginning of the week in ISO which is 1~7, we can get the first day of the week
    true_begin = begin_of_the_month.shift(days=-7)
    for date in arrow.Arrow.range('day', true_begin.datetime, begin_of_the_month.datetime):
        if date.isoweekday() == start_of_week_iso:
            true_begin = date
            break
    true_end = end_of_the_month.shift(days=7)
    for date in arrow.Arrow.range('day', end_of_the_month.datetime, true_end.datetime):
        if date.isoweekday() == start_of_week_iso:
            true_end = date
            break
    date_list = [date.format('YYYY-MM-DD-W') for date in arrow.Arrow.range('day', true_begin.datetime,
                                                                           true_end.datetime)]
    return date_list


if __name__ == '__main__':
    for year in range(2019, 2021):
        for month in range(1, 13):
            print(get_true_monthly_date_span(year, month, 7))
