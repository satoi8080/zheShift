# my-shift

* Part of the source code is modified from [Quickstarts overview](https://github.com/gsuitedevs/python-samples/blob/master/calendar/quickstart/quickstart.py)

## Instructions:

* [Create a project](https://developers.google.com/workspace/guides/create-project)


* [Create OAuth credentials](https://developers.google.com/workspace/guides/create-credentials)


* Rename downloaded credentials file to `credentials.json` and put it into root directory of this project


* Get import and export calendar ID in 

```
Calendar Settings -> Integrate calendar -> Calendar ID
```

* Create a `.env` in root directory of this project and set up as following
```
IMPORT_CALENDAR_ID=
EXPORT_CALENDAR_ID=
TIMEZONE = 'Asia/Tokyo'
CLEAR_OLD_EXPORT = False
ADD_NEW_EXPORT = False
MONTH_OFFSET = 0
QUERY_NAME = 張
```

### Run with docker-compose

`docker-compose up --build --force-recreate -d`

### Run with Python

* Create venv

`python3 -m venv ./venv`

* Activate venv 

`source ./venv/bin/activate`

* RUn

`python3 app.py`