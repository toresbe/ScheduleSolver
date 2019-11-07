class ScheduleItem:
    def __init__(self, start_time, duration):
        self.start_time = start_time
        self.duration = duration

    @property
    def end_time(self):
        return self.start_time + self.duration

    @property
    def microseconds(self):
        return (self.duration.seconds * 1000) + self.duration.microseconds

class ScheduledVideo(ScheduleItem):
    def __repr__(self):
        return 'ScheduledVideo ({}-{}): {}'.format(
                self.start_time.strftime("%H:%M:%S"),
                self.end_time.strftime("%H:%M:%S"),
                self.title)

class PlaceholderGap(ScheduleItem):
    def __repr__(self):
        return 'PlaceholderGap ({}-{}): ({}s)'.format(
                self.start_time.strftime("%H:%M:%S"),
                self.end_time.strftime("%H:%M:%S"),
                self.duration
                )

