import sys
import logging
from oauth2client import client
from googleapiclient import sample_tools
from events import get_events


def do_delete(service, calendar_id, prefix):
    result = service.events().list(calendarId=calendar_id).execute()

    for event in result['items']:
        if event['summary'].startswith(prefix):
            service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
            print('Deleted %s' % event['summary'])


def do_create(service, calendar_id, events, timezone, reminder_offset):
    for event in events:
        try:
            json = create_json(event, timezone, reminder_offset)
            service.events().insert(calendarId=calendar_id, body=json).execute()
            print('Added %s' % event)
        except client.AccessTokenRefreshError:
            print('The credentials have been revoked or expired, please re-run'
                  'the application to re-authorize.')


def create_json(event, timezone, reminder_offset):
    dt_format = '%Y-%m-%dT%H:%M:%S'

    return {
        "summary": event.summary,
        "start": {
            "dateTime": event.start.strftime(dt_format),
            "timeZone": timezone
        },
        "end": {
            "dateTime": event.end.strftime(dt_format),
            "timeZone": timezone
        },
        "reminders": {
            "useDefault": False,
            "overrides": [{
                "minutes": reminder_offset,
                "method": "email"
            }]
        }
    }


def get_service():
    service, _flags = sample_tools.init(
        [''], 'calendar', 'v3', __doc__, __file__,
        scope='https://www.googleapis.com/auth/calendar')
    return service
