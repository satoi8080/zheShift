import os
from dotenv import load_dotenv
from distutils.util import strtobool

load_dotenv()
import_calendar_ID = os.getenv('IMPORT_CALENDAR_ID')
export_calendar_ID = os.getenv('EXPORT_CALENDAR_ID')
export_calendar_URL = os.getenv('EXPORT_CALENDAR_URL')
query_name = os.getenv('QUERY_NAME')
timezone = os.getenv('TIMEZONE')

EIGHT_HOUR_SHIFT = strtobool(os.getenv('EIGHT_HOUR_SHIFT'))

EARLY_START_TIME = '09:00'
MID_START_TIME = '12:00'
LATE_START_TIME = '12:00' if EIGHT_HOUR_SHIFT else '15:00'

