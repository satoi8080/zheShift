import os
from dotenv import load_dotenv

load_dotenv()
read_calendar_ID = os.getenv('CALENDAR_ID')
export_calendar_ID = os.getenv('EXPORT_CALENDAR_ID')
myname = os.getenv('MY_NAME')
timezone = os.getenv('TIMEZONE')
