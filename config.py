import os
from dotenv import load_dotenv
from distutils.util import strtobool

load_dotenv()
import_calendar_ID = os.getenv('IMPORT_CALENDAR_ID')
export_calendar_ID = os.getenv('EXPORT_CALENDAR_ID')
queryname = os.getenv('QUERY_NAME')
timezone = os.getenv('TIMEZONE')

clear_old_export = strtobool(os.getenv('CLEAR_OLD_EXPORT'))
add_new_export = strtobool(os.getenv('ADD_NEW_EXPORT'))
month_offset = int(os.getenv('MONTH_OFFSET'))

EIGHT_HOUR_SHIFT = strtobool(os.getenv('EIGHT_HOUR_SHIFT'))

EARLY_START_TIME = '09:00'
MID_START_TIME = '12:00'
LATE_START_TIME = '12:00' if EIGHT_HOUR_SHIFT else '15:00'
