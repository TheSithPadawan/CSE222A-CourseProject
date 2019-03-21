import socketserver
from queue import Queue
import threading
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
import json
import time
import sys
import os
from os import listdir
from os.path import isfile, join
import random 
import argparse
import requests

# from worker import DummyWorker
from urllib.parse import urlparse

base = '/users/Impetus/data/'
onlyfiles = [f for f in listdir(base) if isfile(join(base, f))]

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

class MyHandler(BaseHTTPRequestHandler):
        
    def do_GET(self):
        ts = time.time()
        # self.path is the parameter
        paths = {
            '/foo': {'status': 200},
            '/bar': {'status': 302},
            '/baz': {'status': 404},
            '/qux': {'status': 500}
        }

        delay_time, data = self.handle_one()
        try:
            self.send_response(200)
            self.send_header("Set-Cookie", "foo=bar")
            self.end_headers()

            self.respond({'delays': delay_time, 'data': data})
            print (threading.currentThread().getName(), "finished :", round(time.time()-ts, 4))
        except:
            print (threading.currentThread().getName(), "broken :", round(time.time()-ts, 4))
        return 

    def handle_one(self):
        query = urlparse(self.path).query
        query_component = dict(qc.split('=') for qc in query.split('&'))
        type_args = query_component['type']
        data = str()
        delay_time = 0
        if type_args == 'hc':
            delay_time = 0
        else:
            delay_time += self.process_request_sigmoid(int(type_args))
            # Who knows wtf its reasonable or not
            # io_args = min(int(int(type_args)/160*6), 5)
            # delay_time += self.dummy_io_job(int(type_args))
        return delay_time, data

    def respond(self, json_data):
        data = json.dumps(json_data)
        self.wfile.write(bytes(data, 'UTF-8'))

    def process_request(self, x):
        # impose a maximum time limit for the request 
        MAX_TIMELIMIT = (3*100**3 + 2*100**2 + 100 * 10**5) * 1.5
        base = 3*x**3 + 2*x**2 + x + 10**5
        variation = random.uniform(0.9, 1.1)
        final = int(base * variation)
        if x >= 150:
            final = MAX_TIMELIMIT
        dummy = 0
        start_time = time.time()
        for i in range(final):
            dummy += 1
        end_time = time.time()
        # if self.debug:
            # print ('current request with param', x, 'has been processed for', end_time - start_time,'seconds')
        return end_time - start_time
      
    def process_request_sigmoid(self, x):
        def customized_sigmoid(x, slope=4):
            # returns a number between 0 - 2
            # x = abs(100-x)*3
            return (x / (1+abs(x)/slope)) / slope + 1
            
        multiplier = customized_sigmoid(x) * 100
        base = 3.5*10**3
        # workload     0.001s - 0.2s
        return self.dummy_job(base*multiplier)

    def dummy_job(self, loop):
        """
        length varies for different type
        total latency = base latency * random in range [0.85 - 1.51)
        # power = 6   # 'HEAVY'     0.1s
        # power = 5   # 'MEDIAN'    0.01s
        # power = 4   # 'LIGHT'     0.001s
        """
        ts = time.time()
        actual = int(loop * random.uniform(0.95, 1.11))
        for i in range(actual):
            a = 1
        return time.time()-ts

    def dummy_io_job(self, x):
        # repeat = min(x * 10, 1000)
        delay = self.read_random_file(x)
        return delay

    def write_to_file(self, repeat=1):
        ts = time.time()
        base = 'tmp/'
        fn = str(random.random())[2:12] + '.txt'
        if not os.path.exists(base):
            os.makedirs(base)
        fp = base+fn
        with open(fp, 'a') as the_file:
            for i in range(repeat):
                the_file.write(str(random.random()))
        os.remove(fp)
        return round(time.time()-ts,5)

    # def read_random_file(self, size):
    #     fn = base+random.choice(onlyfiles)
    #     ts = time.time()
    #     with open(fn, 'r', errors='ignore') as content_file:
    #         size = 10**7*size
    #         content = content_file.read(size)
    #     return round(time.time()-ts, 5)

    def read_random_file(self, size):
        ts = time.time()
        fn = base + 'dummy_file.txt'
        with open(fn, 'r', errors='ignore') as content_file:
            content_file.seek(0,2) # move the cursor to the end of the file
            file_size = content_file.tell()
            content_file.seek(random.randint(0,file_size))
            content = content_file.read(100000*size)
        return round(time.time()-ts,5)


class MyServer():

    HOST_NAME = '0.0.0.0'
    PORT_NUMBER = 5050

    # def start_worker(self, num_of_worker=7, delays=5, work_duration=5, sleep_duration=5):
    #     for x in range(num_of_worker):
    #         dworker = DummyWorker(delays, work_duration, sleep_duration, TTL=1000)
    #         dworker.start()

    def start_server(self, port, hostname):
        self.PORT_NUMBER = port
        self.HOST_NAME = hostname
        HOST_NAME = self.HOST_NAME
        PORT_NUMBER = self.PORT_NUMBER
        
        httpd = ThreadingSimpleServer((HOST_NAME, PORT_NUMBER), MyHandler)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('Server Closed')
            pass
        httpd.server_close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start Backend Server listening to HTTP requests')
    parser.add_argument('-p', '--port', action='store', required=True, dest='port', help='the port that server listens to', type=int)
    parser.add_argument('-hs', '--hostname', action='store', dest='hostname', required=True, help='the host that server binds to', type=str)
    # parser.add_argument('-d', '--delay', action='store', dest='worker_delay', help='seconds that worker delays start', default=5, type=int)
    # parser.add_argument('-l', '--duration', action='store', dest='worker_duration', help='seconds that worker continuesly works', default=5, type=int)
    # parser.add_argument('-s', '--sleep', action='store', dest='worker_sleep', help='seconds that worker breaks between work time', default=5, type=int)
    # parser.add_argument('-n', '--worker', action='store', dest='num_worker', help='number of dummy workers that offer the delay', default=7, type=int)
    args = vars(parser.parse_args())
    server = MyServer()
    # server.start_worker(args['num_worker'], args['worker_delay'], args['worker_duration'], args['worker_sleep'])
    server.start_server(args['port'], args['hostname'])
