import json
import threading
import time
import http.server
import socketserver
import json

from datetime import datetime, timedelta,timezone
from ScheduleFetcher import ScheduleFetcher
from ScheduleGapDetector import ScheduleGapDetector
from ScheduleSolver import ColdstartSolver, ScheduleSolver

class ScheduleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def get_schedule(self):
        schedule = ScheduleFetcher.get_schedule('https://frikanalen.no/api/scheduleitems/')
        schedule = ScheduleGapDetector.insert_gaps(schedule)
        solved_schedule = ScheduleSolver.solve(schedule)
        cold_start = ColdstartSolver.solve(schedule, datetime.now(timezone.utc) + timedelta(seconds=5))
        metadata = {"version": 1}
        schedule_data = {'metadata': metadata, 'schedule': solved_schedule, 'cold_start': cold_start}

        return(json.dumps(schedule_data).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(self.get_schedule())

import atexit

class ScheduleHTTPServer:
    handler = ScheduleHTTPRequestHandler

    def __init__(self, host, port):
        self.server = socketserver.TCPServer((host, port), self.handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True

    def start(self):
        atexit.register(self.stop)
        self.server_thread.start()

    def stop(self):
        print('Schedule HTTP server shutting down')
        self.server.shutdown()
        self.server.server_close()

if __name__ == '__main__':
    port = 8000
    while True:
        try:
            server = ScheduleHTTPServer('localhost', port)

            print('listening on port {}'.format( port))
            server.start()
            while True:
                time.sleep(100)
        except OSError:
            port += 1
            pass
