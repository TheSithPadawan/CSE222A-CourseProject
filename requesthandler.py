import random
import requests
import threading
from abc import ABC, abstractmethod
from http.server import BaseHTTPRequestHandler
from util import upstream_server, upstream_server_status

class RequestHandler(BaseHTTPRequestHandler, ABC):
    connection_count = 0
    
    def do_GET(self):
        print(threading.currentThread().getName(), "get the request, ready to serve")
        RequestHandler.connection_count += 1
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
    """
     A server has a list of all the unique IP addresses that are associated with the Internet domain name. 
     When requests for the IP Address associated with the Internet domain name are received, (we could not do this)
     When requests for the Load Balancer IP Address are received, (we do this instead)
     the addresses are returned in a rotating sequential manner.
    """
    cnt = 0

    def redirect_server_id(self):
        RoundRobinHandler.cnt += 1
        return RoundRobinHandler.cnt%self.num_server

class LeastConnectionHandler(RequestHandler):
    """
     The Least Connection method does take the current server load into consideration. 
     The current request goes to the server that is servicing 
     the least number of active sessions at the current time.
    """
    def redirect_server_id(self):
        # [TODO]
        return 0

class ChainedConnectionHandler(RequestHandler):
    """
     In this method, a predetermined order of servers is configured in a chain. 
     All requests are sent to the first server in the chain. 
     If it can’t accept any more requests the next server in the chain is sent all requests, 
     then the third server. And so on.
    """
    def redirect_server_id(self):
        # [TODO]
        return 0

class LeastLatencyHandler(RequestHandler):
    def redirect_server_id(self):
        min_latency_id = 0
        min_latency = 999
        for serverID in upstream_server_status.keys():
            latency = upstream_server_status[serverID].delays.get()
            # print('print(serverID, latency)', serverID, latency)
            if min_latency > latency:
                min_latency = latency
                min_latency_id = serverID
        # print('min_latency_id', min_latency_id)
        # [TODO] estimate the latency of each type of request
        upstream_server_status[min_latency_id].delays.put(min_latency+0.02) # hard code estimate per request
        # print('LeastLatencyHandler to \t\t\t\t', min_latency_id, '\t\t', round(min_latency,4))
        return min_latency_id
