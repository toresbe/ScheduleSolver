import re
from datetime import timedelta, datetime
from pprint import pprint
from ScheduleItems import ScheduledVideo
import requests
from dateutil.parser import isoparse

class ScheduleFetcher:
    # Creates a Python timedelta object from an ISO 8601
    # duration field, ie HH:MM:SS[.microseconds]
    @staticmethod
    def timedelta_from_iso(isostamp):
        # Add fake microseconds if they're not there
        if '.' not in isostamp:
            isostamp += '.0'

        matchstring = r'(?P<hours>\d{2}):(?P<minutes>\d{2}):'\
                    '(?P<seconds>\d{2}).(?P<microseconds>\d+)'

        regmatches = re.match(matchstring, isostamp).groupdict()

        regmatches = {x: int(y) for x, y in regmatches.items()}

        return timedelta(**regmatches)

#    # Creates a Python datetime object from an ISO 8601
#    # date-time field, eg '2019-11-01T03:39:00.0Z'
#    @staticmethod
#    def datetime_from_iso(isostamp):
#        # I can't believe you have to do this, but strptime doesn't
#        # support ISO 8601 time zone spec so...
#        if '.' not in isostamp:
#            # the code underneath assumes Zulu time so if the
#            # API changes, we really need to raise a red flag
#            assert(isostamp[-1] == 'Z')
#            isostamp = isostamp[:-1] + '.0Z'
#
#        return datetime.strptime(isostamp, '%Y-%m-%dT%H:%M:%S.%fZ')

    # Fetches the Frikanalen schedule from the given URI and returns
    # a list of ScheduledVideo objects.
    @staticmethod
    def get_schedule(uri):
        r = requests.get(uri, params = {'page_size':100000, 'days': 2}).json()

        schedule = []
        a = 0
        for x in r['results']:
            start_time = isoparse(x['starttime'])
            duration = ScheduleFetcher.timedelta_from_iso(x['duration'])

            event = ScheduledVideo(start_time, duration)
            # this is really just so the proof of concept playout
            # can play back using ogg theora files
            event.ogv_url = x['video']['ogv_url']
            event.framerate = x['video']['framerate']
            event.title = x['video']['name']
            schedule.append(event)

        return schedule

if __name__ == '__main__':
    print(ScheduleFetcher.get_schedule('https://frikanalen.no/api/scheduleitems/'))
