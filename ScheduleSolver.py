from ScheduleItems import ScheduledVideo, PlaceholderGap

class AMCPMedia:
    def __repr__(self):
        return 'AMCPMedia[layer={}, channel={}]'.format(self.layer, self.channel)

    def __init__(self, channel, layer):
        self.channel = channel
        self.layer = layer

    def play(self, path, loop=False, seek=None):
        cmd = 'PLAY {}-{} "{}"'.format(self.channel, self.layer, path)
        if loop:
            cmd += ' LOOP'
        if seek is not None:
            cmd += ' SEEK {}'.format(seek.seconds)
        return cmd

    def clear(self):
        return 'CLEAR {}-{}'.format(self.channel, self.layer)

class AMCPCG:
    def __repr__(self):
        return 'AMCPCG[layer={}, channel={}]'.format(self.layer, self.channel)

    def __init__(self, channel, layer=9999, cg_layer=0):
        self.channel = channel
        self.layer = layer
        self.cg_layer = cg_layer

    def add(self, uri, play_on_load=False, json_data=None):
        return 'CG {}-{} ADD {} "{}" {} {}'.format(
                self.channel,
                self.layer,
                self.cg_layer,
                uri,
                int(play_on_load),
                json_data or '')

    def play(self):
        return 'CG {}-{} PLAY {}'.format(
                self.channel,
                self.layer,
                self.cg_layer)

    def stop(self):
        return 'CG {}-{} STOP {}'.format(
                self.channel,
                self.layer,
                self.cg_layer)


class ScheduledVideoHandler:
    def __init__(self, device, transport):
        self.transport = transport
        self.device = device

    #TODO: Make a meaningfully different cold_start function
    # so there is no BUG whereby the clear message is doubled
    # (hopefully harmlessly, but it might create a race condition)
    def handle(self, video: ScheduledVideo, seek=None):
        commands = [
                {
                    'device_idx': self.device.idx,
                    'timestamp': video.start_time.isoformat(),
                    'command': self.transport.play(video.ogv_url, seek=seek),
                    'debug': '{} playing video [{}]'.format(self, video.title),
                },
                {
                    'device_idx': self.device.idx,
                    'timestamp': video.end_time.isoformat(),
                    'command': self.transport.clear(),
                    'debug': repr(self) + ' stopping video',
                }
        ]
        return commands

    def __repr__(self):
        return 'GraphicsHandler [mcr_device={}, transport={}]'.format(self.device, self.transport)

class MCRDevice():
    def __init__(self, idx):
        self.idx = idx

    def __repr__(self):
        return 'MCRDevice[{}]'.format(self.idx)

class GraphicsHandler(AMCPMedia):
    def __init__(self, mcr_device, transport):
        self.device = mcr_device
        self.transport = transport

    def handle(self, gap: PlaceholderGap):

        commands = [
                {
                    'device_idx': self.device.idx,
                    'timestamp': (gap.start_time - timedelta(seconds=10)).isoformat(),
                    'command': self.transport.add('http://simula.gunkies.org/~toresbe/progpres/index.html?duration=' + gap.microseconds),
                    'debug': repr(self) + ' loading CG',
                },
                {
                    'device_idx': self.device.idx,
                    'timestamp': gap.start_time.isoformat(),
                    'command': self.transport.play(),
                    'debug': repr(self) + ' entering CG',
                },
                {
                    'device_idx': self.device.idx,
                    'timestamp': (gap.end_time - timedelta(seconds=.5)).isoformat(),
                    'command': self.transport.stop(),
                    'debug': repr(self) + ' clearing CG',
                }
        ]

        return commands

    def __repr__(self):
        return 'GraphicsHandler [mcr_device={}, transport={}]'.format(self.device, self.transport)


class ScheduleSolver:
    handlers = {
        ScheduledVideo: ScheduledVideoHandler(MCRDevice(0), AMCPMedia(channel=1, layer=100)),
        PlaceholderGap: GraphicsHandler(MCRDevice(0), AMCPCG(channel=1)),
    }

    @staticmethod
    def solve(schedule):
        commands = []
        for item in schedule:
            handler = ScheduleSolver.handlers.get(type(item))
            #print(type(item), item)
            for cmd in handler.handle(item):
                commands.append(cmd)
        commands = sorted(commands, key = lambda i: i['timestamp'])
        return commands

class ColdstartSolver(ScheduleSolver):
    @staticmethod
    def get_currently_playing_item(schedule, cold_start_time):
        #print(schedule)
        for item in schedule:
            #print(item.end_time, cold_start_time)
            if item.end_time < cold_start_time:
                continue
            #print(item)
            # We only support generating state for
            # scheduled video so far
            #print(type(item))
            if isinstance(item, ScheduledVideo):
                print('Cold-starting: {}'.format(item))
                return item

    @staticmethod
    def solve(schedule, cold_start_time):
        item = ColdstartSolver.get_currently_playing_item(schedule, cold_start_time)
        handler = ScheduleSolver.handlers.get(type(item))
        commands = handler.handle(item, seek=(cold_start_time - item.start_time) * item.framerate)

        return commands

if __name__ == '__main__':
    import json
    from ScheduleFetcher import ScheduleFetcher
    from ScheduleGapDetector import ScheduleGapDetector
    schedule = ScheduleFetcher.get_schedule('https://frikanalen.no/api/scheduleitems/')
    schedule = ScheduleGapDetector.insert_gaps(schedule)
    solved_schedule = ScheduleSolver.solve(schedule)
    cold_start = ColdstartSolver.solve(schedule)

    metadata = {"version": 1}
    schedule_data = {'metadata': metadata, 'schedule': solved_schedule, 'cold_start': cold_start}

    print(json.dumps(schedule_data))
