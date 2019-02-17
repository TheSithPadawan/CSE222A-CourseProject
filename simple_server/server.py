import socketserver
from queue import Queue
from http.server import BaseHTTPRequestHandler,HTTPServer
import json
import time

from worker import QueryWorker, DummyWorker, MonitorWorker

class MyHandler(BaseHTTPRequestHandler):
        
    def do_GET(self):
        # self.path is the parameter
        paths = {
            '/foo': {'status': 200},
            '/bar': {'status': 302},
            '/baz': {'status': 404},
            '/qux': {'status': 500}
        }

        # print("\n----- Request Start ----->\n")
        # print("request_path :", self.path)
        # print("self.headers :", self.headers)
        # print("<----- Request End -----\n")
        
        self.send_response(200)
        self.send_header("Set-Cookie", "foo=bar")
        self.end_headers()

        # [TODO] how to get data sent back to HTTP
        self.handle_one()

        # if self.path in paths:
            # self.respond(paths[self.path])
        # else:
            # self.respond({'status': 500})

    def handle_one(self):
        queue.put(self)

    def respond(self, json_data):
        # print(json_data)
        data = json.dumps(json_data)
        # print('data sent:', data)
        # print("\n<----- Respond End -----\n")
        self.wfile.write(bytes(data, 'UTF-8'))

class MyServer():

    HOST_NAME = 'localhost'
    PORT_NUMBER = 9000

    def start_worker(self, queue):
        start = time.time()
        delays = list()

        # Create query worker
        ts = time.time()

        qworker = QueryWorker(queue, delays, ts)
        qworker.daemon = True
        qworker.start()

        # Create 7 dummy worker threads
        for x in range(7):
            dworker = DummyWorker(x, 1000)
            dworker.daemon = True
            dworker.start()
            
        # monitor = MonitorWorker()
        # monitor.start()
        queue.join()
        end = time.time()

    def start_server(self):
        HOST_NAME = self.HOST_NAME
        PORT_NUMBER = self.PORT_NUMBER

        server_class = HTTPServer
        httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('Server Closed')
            pass
        httpd.server_close()

queue = Queue()
server = MyServer()
server.start_worker(queue)
server.start_server()