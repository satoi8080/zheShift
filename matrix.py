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

def get_true_monthly_date_span(year: int, month: int, iso_start_of_week: int,
                               begin_and_end_only: bool = False) -> list:
    begin_of_the_month = arrow.get(f'{year}-{month}-01')
    end_of_the_month = begin_of_the_month.shift(months=1).shift(days=-1)
    # Get the date span range extended days according to the beginning of week given
    # With the beginning of the week in ISO which is 1~7, we can get the first day of the week
    true_begin = begin_of_the_month.shift(days=-6)
    for date in list(arrow.Arrow.range('day', true_begin.datetime, begin_of_the_month.datetime))[::-1]:
        if date.isoweekday() == iso_start_of_week:
            true_begin = date
            break
    true_end = end_of_the_month.shift(days=6)
    for date in list(arrow.Arrow.range('day', end_of_the_month.datetime, true_end.datetime)):
        if date.isoweekday() == iso_start_of_week:
            true_end = date
            break
    date_list = [date.format('YYYY-MM-DD') for date in arrow.Arrow.range('day', true_begin.datetime, true_end.datetime)]

    if begin_and_end_only:
        return [true_begin.format('YYYY-MM-DD-dddd'), true_end.format('YYYY-MM-DD-dddd')]
    else:
        return date_list


if __name__ == '__main__':
    for _year in [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]:
        for _month in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
            print(f'{_year}-{_month}')
            print(get_true_monthly_date_span(year=_year, month=_month, iso_start_of_week=1))
