# eventbrite-automation

Project to automate some repetitive tasks while trying to coordinate a security conference. Right now the script just updates a google sheet with attendee names and email addresses.

## Install

1. Create a .env file:

```
EVENTBRITE_API_KEY = '<EVENTBRITE API PRIVATE TOKEN>'
EVENT_ID = 
CREDENTIALS_PATH = 'GOOGLE API PRIVATE KEY CREDENTIALS JSON'
WORKSHOPS_YAML = 'workshops.yaml'
```

2. Create Credentials file using an openauth service account from the Google sheets API

3. Create a Google sheet for each workshop or ticket type you want to track. Sheet is in the google sheet URL. Make sure to give the account in your credentials access to the google sheets

4. Workshop yaml has the following format with details from eventbrite. Workshop title is just for readability, the script will get the exact ticket title from eventbrite:

```
workshops:
  - name: 'Web App Hacking' 
    id: 2373242
    sheet_id: ''
```

5. Install dependencies `pipenv install`

## Run

`pipenv run python main.py`