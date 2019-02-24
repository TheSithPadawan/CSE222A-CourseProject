import requests
import threading
import time
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from util import upstream_server, upstream_server_status
from requesthandler import (
    RandomHandler,
    RoundRobinHandler,
    LeastConnectionHandler,
    ChainedConnectionHandler,
    LeastLatencyHandler
    )

"""
main program:
main thread: accept connection 
when a connection is accepted, use thread
to do the work:
    copy each http request
    forward to upstream server in a roundrobin fashion 
"""

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

class LoadBalancerServer():
    HOST_NAME = 'localhost'
    PORT_NUMBER = 8080
    REQUESTHANDLER = RoundRobinHandler        # Change Load Balancing Algorithm

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
            upstream_server_status[serverID].delays.put(latency)
        
if __name__ == "__main__":
    lb = LoadBalancerServer()
    lb.start_healthcheck()
    lb.start_server()            
            
