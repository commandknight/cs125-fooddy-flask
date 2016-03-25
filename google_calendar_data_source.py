from __future__ import print_function
import httplib2
import os

import pprint as pp
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime

try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# To test with your own calendar, run this on sterminal: python google_calendar_data_source.py --noauth_local_webserver


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'resources/google_calendar_client_secret.json'
APPLICATION_NAME = 'Fooddy - Your Food Buddy'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_next_event_timedateloc_on_google_calendar(credentials):
    """Shows basic usage of the Google Calendar API.
    :param credentials
    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    # credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the next event')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=1, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    # for event in events:
    start = events[0]['start'].get('dateTime', events[0]['start'].get('date'))
    name = events[0]['summary']
    if 'location' in events[0].keys():
        location = events[0]['location']

    return events[0]['summary']
    # return start + "--" + name + "--" + location (RETURNS SIMPLE STRING SEPARATED BY "--")


if __name__ == '__main__':
    event_string = get_next_event_timedateloc_on_google_calendar()
    pp.pprint(event_string)
