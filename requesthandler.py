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
     The server continuously rotates a list of the services that are bound to it. 
     When the virtual server receives a request, it assigns the connection to the first service in the list, 
     and then moves that service to the bottom of the list.
     [RESOURCE] https://docs.citrix.com/en-us/netscaler/12/load-balancing/load-balancing-customizing-algorithms/roundrobin-method.html
    """
    cnt = 0

    def redirect_server_id(self):
        # [TODO] handle non 0/1 cases
        RoundRobinHandler.cnt += 1
        return RoundRobinHandler.cnt%self.num_server

class LeastConnectionHandler(RequestHandler):
    """
     The Least Connection method does take the current server load into consideration. 
     The server selects the service with the fewest active connections. 
     This is the default method, because, in most circumstances, it provides the best performance.
     [RESOURCE] https://docs.citrix.com/en-us/netscaler/12/load-balancing/load-balancing-customizing-algorithms/leastconnection-method.html
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
     [RESOURCE] https://kemptechnologies.com/glossary/load-balancing-methods/
    """
    def redirect_server_id(self):
        # [TODO]
        return 0

class LeastPacketsHandler(RequestHandler):
    """
     A load balancing virtual server configured to use the least packets method
     selects the service that has received the fewest packets in the last x seconds.
     [RESOURCE] https://docs.citrix.com/en-us/netscaler/12/load-balancing/load-balancing-customizing-algorithms/leastpackets-method.html
     [RESOURCE] MAYBE use psutil.net_io_counters(pernic=False)?
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