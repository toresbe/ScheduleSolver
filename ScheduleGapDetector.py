from datetime import timedelta
from ScheduleItems import PlaceholderGap

class ScheduleGapDetector:
    """Insert placeholder gap items in the schedule which can be conveniently
    retreived later"""
    @staticmethod
    def insert_gaps(schedule):
        gaps = []
        i = 1

        this_vid = schedule[0]
        #print(len(schedule))
        # TODO: Spin the actual gap creation into a
        # new_gap = make_gap_between(prev_vid, this_vid)
        while(i < len(schedule)):
            prev_vid = this_vid
            this_vid = schedule[i]
            i+=1 # no gap before first item in schedule
            gap_duration = this_vid.start_time - prev_vid.end_time
            if(gap_duration > timedelta(seconds=3)):
                gap = PlaceholderGap(prev_vid.end_time, gap_duration)
                #print('filling gap from {} to {}'.format(prev_vid.end_time, this_vid.start_time))
                #print('inserting {} into schedule[{}]'.format(gap, i))

                schedule.insert(i, gap)
                i+=1
            else:
                pass
                #print('not inserting gap as duration {} too short'.format(gap_duration))

        return schedule

if __name__ == '__main__':
    from ScheduleHTTPClient import VideoFetcher

    schedule = VideoFetcher.get_schedule('https://frikanalen.no/api/scheduleitems/')

    try:
        from pprint import pprint
        pprint(ScheduleGapDetector.insert_gaps(schedule))
    except ImportError:
        print(ScheduleGapDetector.insert_gaps(schedule))
