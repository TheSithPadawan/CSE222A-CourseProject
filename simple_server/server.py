import socketserver
from queue import Queue
from http.server import BaseHTTPRequestHandler,HTTPServer
import json
import time
import sys

from worker import QueryWorker, DummyWorker, MonitorWorker
from urllib.parse import urlparse

class HttpRequest:
    body = dict()
    def __init__(self, path, parameter):
        self.body['path'] = path
        self.body['type'] = parameter

"""
Three types of requests:
parameter a, b and c 
request format: http://localhost:port/foo?type=(a, b, c)
"""
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
        # print("request_path :", self.bpath)
        # print("self.headers :", self.headers)
        # print("<----- Request End -----\n")
        
        # [TODO] how to get data sent back to HTTP
        self.handle_one()

        self.send_response(200)
        self.send_header("Set-Cookie", "foo=bar")
        self.end_headers()
        # if self.path in paths:
            # self.respond(paths[self.path])
        # else:
            # self.respond({'status': 500})

    def handle_one(self):
        query = urlparse(self.path).query
        query_component = dict(qc.split('=') for qc in query.split('&'))
        type_args = query_component['type']
        r = HttpRequest(self.path, type_args) 
        queue.put(r)

    def respond(self, json_data):
        # print(json_data)
        data = json.dumps(json_data)
        # print('data sent:', data)
        # print("\n<----- Respond End -----\n")
        self.wfile.write(bytes(data, 'UTF-8'))

class MyServer():

    HOST_NAME = 'localhost'
    PORT_NUMBER = 0

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

    def start_server(self, port):
        self.PORT_NUMBER = port
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

if __name__ == "__main__":
    queue = Queue()
    server = MyServer()
    server.start_worker(queue)
    server.start_server(int(sys.argv[1]))
