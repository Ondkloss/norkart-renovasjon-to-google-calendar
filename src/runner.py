import sys
import logging
import processor
import inserter
from events import get_events


if __name__ == "__main__":
    dry_run = False
    if len(sys.argv) == 2 and sys.argv[1] == '--dry-run':
        dry_run = True

    config = processor.read_config('config.ini')
    i = config['internal']
    k = config['geonorge-json']
    r = config['renovation-api']
    c = config['google-calendar']

    municipality_number = processor.get_municipality_number(k['municipality'])
    url = processor.get_renovation_pdf_url(r['api-key'], municipality_number, r['street-name'], r['street-number'], r['year'])
    processor.create_renovation_csv(url, i['csv-filename'])
    events = get_events(i['csv-filename'], c['event-title-prefix'], int(r['year']), int(c['event-start-hour']))

    if not dry_run:
        service = inserter.get_service()
        inserter.do_create(service, c['calendar-id'], events, c['event-timezone'], c['reminder-offset'])
    else:
        for event in events:
            print('Added %s' % event)
