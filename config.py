import os
from dotenv import load_dotenv

load_dotenv()
import_calendar_ID = os.getenv('IMPORT_CALENDAR_ID')
export_calendar_ID = os.getenv('EXPORT_CALENDAR_ID')
queryname = os.getenv('QUERY_NAME')
timezone = os.getenv('TIMEZONE')
