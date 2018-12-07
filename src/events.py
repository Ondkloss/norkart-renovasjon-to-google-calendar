import logging
import csv
import dateutil.tz
import datetime


class Event:
    def __init__(self, summary, start, end):
        self.summary = summary
        self.start = start
        self.end = end

    def __lt__(self, other):
        return self.start < other.start

    def __repr__(self):
        return '<%s, %s, %s>' % (self.summary, self.start, self.end)


def get_events(filename, prefix, year, start_hour):
    result = []
    with open(filename, newline='') as csvfile:
        dictionary = csv.DictReader(csvfile)
        for row in dictionary:
            for key in row:
                if row[key] and key != 'Uke':
                    _weekday, date = row[key].split(' ')
                    day, month = date.split('.')
                    start = datetime.datetime(year, int(month), int(day), start_hour)
                    end = start + datetime.timedelta(hours=1)
                    exists = False

                    for i in range(max(0, len(result)-len(row)), len(result)):
                        if result[i].start == start:
                            result[i].summary += ' + '+key
                            exists = True
                            break

                    if not exists:
                        result.append(Event(prefix+' '+key, start, end))

    return sorted(result)
