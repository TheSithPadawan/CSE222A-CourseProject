from abc import ABC, abstractmethod
import requests
import threading
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
import random
import time
from util import MaxQueue

"""
main program:
main thread: accept connection 
when a connection is accepted, use thread
to do the work:
    copy each http request
    forward to upstream server in a roundrobin fashion 
"""

connection_count = 0
upstream_server = {
    0: "http://127.0.0.1:5050",
    1: "http://127.0.0.1:6000"
    }
upstream_server_status = {
    0: MaxQueue(),
    1: MaxQueue()
}

class RequestHandler(BaseHTTPRequestHandler, ABC):

    def do_GET(self):
        global connection_count
        print (threading.currentThread().getName(), "get the request, ready to serve")
        connection_count += 1
        self.num_server = len(upstream_server)

        # select next server bsaed on different implementation
        server_id = self.redirect_server_id()

        addr = upstream_server[server_id]+self.path
        # post the request
        r = requests.get(addr, headers=self.headers)
        self.send_response(r.status_code)
        self.end_headers()
        self.wfile.write(bytes(r.text, 'UTF-8'))

    @abstractmethod
    def redirect_server_id(self):
        pass

class RandomHandler(RequestHandler):
    
    def redirect_server_id(self):
        return random.randint(0, self.num_server-1)

class RoundRobinHandler(RequestHandler):
    
    def redirect_server_id(self):
        return connection_count%self.num_server

class OneServerHandler(RequestHandler):
    
    def redirect_server_id(self):
        return 0

class LeastLatencyHandler(RequestHandler):
    
    def redirect_server_id(self):
        min_latency_id = 0
        min_latency = 999
        for serverID in upstream_server_status.keys():
            latency = upstream_server_status[serverID].get()
            # print('print(serverID, latency)', serverID, latency)
            if min_latency > latency:
                min_latency = latency
                min_latency_id = serverID
        # print('min_latency_id', min_latency_id)
        upstream_server_status[serverID].put(min_latency+0.02) #estimate per request
        # print('LeastLatencyHandler to \t\t\t\t', min_latency_id, '\t\t', round(min_latency,4))
        return min_latency_id

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

class LoadBalancerServer():
    HOST_NAME = 'localhost'
    PORT_NUMBER = 8080
    REQUESTHANDLER = LeastLatencyHandler        # Change Load Balancing Algorithm

    def start_server(self):
        HOST_NAME = self.HOST_NAME
        PORT_NUMBER = self.PORT_NUMBER
        print('LB uses handler: ', str(self.REQUESTHANDLER.__name__))
        httpd = ThreadingSimpleServer((HOST_NAME, PORT_NUMBER), self.REQUESTHANDLER)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('Server Closed')
            pass
        httpd.server_close()

    def start_healthcheck(self):
        endpoints = [(key, ip+'/foo?type=hc') for (key, ip) in upstream_server.items()]
        print(endpoints)
        for serverID, endpoint in endpoints:
            print(endpoint)
            thread = threading.Thread(target=self.get_server_latency, args = (endpoint, serverID))
            thread.start()
        

    def get_server_latency(self, endpoint, serverID, frequency=0.1):
        while True:
            time.sleep(frequency)
            ts = time.time()
            try:
                requests.get(endpoint)
            except:
                raise Exception("Endpoint not accessiable, start backend server first!")
                break
            latency = time.time() - ts
            upstream_server_status[serverID].put(latency)
        
if __name__ == "__main__":
    lb = LoadBalancerServer()
    lb.start_healthcheck()
    lb.start_server()            
            
