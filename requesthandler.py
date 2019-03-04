import random
import requests
import threading
import time
from abc import ABC, abstractmethod
from http.server import BaseHTTPRequestHandler
from util import (
    upstream_server, 
    upstream_server_status,
    get_timestamp
    )
from requests.exceptions import (
    ConnectionError,
    ConnectTimeout,
    ReadTimeout,
    Timeout
    )

class RequestHandler(BaseHTTPRequestHandler, ABC):
    connection_count = 0
    TIME_OUT = 3
    
    def do_GET(self):
        ts = time.time()

        RequestHandler.connection_count += 1
        self.num_server = len(upstream_server)

        while self.TIME_OUT > 0:
            try:
                # select next server bsaed on different implementation
                server_id = self.redirect_server_id()
                endpoint = upstream_server[server_id]+self.path

                r = self.redirect_request(server_id, endpoint)

                self.send_response(r.status_code)
                self.end_headers()
                self.wfile.write(bytes(r.text, 'UTF-8'))
                return

            except Timeout:
                print(get_timestamp('RequestHandler'), 'TIME_OUT')
                # when there is an connection time out
                # send back error code
                break

            except Exception as e:
                print(get_timestamp('RequestHandler'))
                print(e, end='\n\n')
                # when there is an connection error resend request
                # going to try again after 0.5s 
                # (ps, if try again immediately, will likely comes to connection error again)
                print('Exception, Retransmission required')
                # time.sleep(0.5)
                # self.TIME_OUT -= 0.5              

            self.TIME_OUT -= time.time()-ts
        
        print(get_timestamp('RequestHandler'), 'Sends back 504')
        self.send_response(504)
        self.end_headers()

    @abstractmethod
    def redirect_server_id(self):
        pass

    @abstractmethod
    def redirect_request(self, server_id, endpoint):
        pass

class RandomHandler(RequestHandler):
    #handled the server failure     
    def redirect_server_id(self): 
        serverID = random.randint(0, self.num_server-1)
        while (upstream_server_status[serverID].alive ==False):
            serverID = random.randint(0, self.num_server-1)
        return serverID    

    def redirect_request(self, server_id, endpoint):
        return requests.get(endpoint, headers=self.headers, timeout=self.TIME_OUT)

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
        while True:
            server_id = RoundRobinHandler.cnt % self.num_server
            RoundRobinHandler.cnt += 1
            if upstream_server_status[server_id].alive ==False:
                continue
            else:
                break
        return server_id

    def redirect_request(self, server_id, endpoint):
        return requests.get(endpoint, headers=self.headers, timeout=self.TIME_OUT)

class LeastConnectionHandler(RequestHandler):
    """
     The Least Connection method does take the current server load into consideration. 
     The server selects the service with the fewest active connections. 
     This is the default method, because, in most circumstances, it provides the best performance.
     [RESOURCE] https://docs.citrix.com/en-us/netscaler/12/load-balancing/load-balancing-customizing-algorithms/leastconnection-method.html
    """

    def redirect_server_id(self):
        server = None
        minimum = None
        for serverID in upstream_server_status.keys():
            if upstream_server_status[serverID].alive ==True:
                if minimum==None or upstream_server_status[serverID].workloads < minimum :
                    minimum = upstream_server_status[serverID].workloads
                    server = serverID

        return server

    def redirect_request(self, server_id, endpoint):
        try:
            upstream_server_status[server_id].workloads += 1
            r = requests.get(endpoint, headers=self.headers, timeout=self.TIME_OUT)
            upstream_server_status[server_id].workloads -= 1
        except (ConnectionError, ConnectTimeout, ReadTimeout) as error:
            upstream_server_status[server_id].workloads -= 1
            raise error
        return r

class ChainedConnectionHandler(RequestHandler):
    """
     In this method, a predetermined order of servers is configured in a chain. 
     All requests are sent to the first server in the chain. 
     If it can’t accept any more requests the next server in the chain is sent all requests, 
     then the third server. And so on.
     [RESOURCE] https://kemptechnologies.com/glossary/load-balancing-methods/
    """
    cnt = 0
    weight =10

    def redirect_server_id(self):
        while True:
            server_id = (ChainedConnectionHandler.cnt // self.weight)%self.num_server
            ChainedConnectionHandler.cnt += 1
            if upstream_server_status[server_id].alive ==False:
                ChainedConnectionHandler.cnt += self.weight
            else:
                break
        return server_id

    def redirect_request(self, server_id, endpoint):
        return requests.get(endpoint, headers=self.headers, timeout=self.TIME_OUT)

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
    """
     Least Latency chooses server which replies the server health check first
     If servers reply with same timestamp, compare the health check latency
     Add an additional avg letency to the selected server
    """
    def redirect_server_id(self):
        server_id = 0
        min_latency = 999
        max_ts = 0

        for serverID in upstream_server_status.keys():
            if upstream_server_status[serverID].alive ==True:
                ts, latency = upstream_server_status[serverID].delays.get()
                if max_ts < ts:
                    max_ts = ts
                    min_latency = latency
                    server_id = serverID
                elif max_ts == ts and min_latency > latency:
                    min_latency = latency
                    server_id = serverID
        # print('------------------------------------------------------')
        # print('server 0 estimate', upstream_server_status[0].avglatency.get())
        # print('server 0 ts', upstream_server_status[0].delays.get()[0])
        # print('server 0 delay', upstream_server_status[0].delays.get()[1])
        # print('server 1 estimate', upstream_server_status[1].avglatency.get())
        # print('server 1 ts', upstream_server_status[1].delays.get()[0])
        # print('server 1 delay', upstream_server_status[1].delays.get()[1])
        # print('sent to server', server_id)
        return server_id

    def redirect_request(self, server_id, endpoint):
        ts, latency = upstream_server_status[server_id].delays.get()
        # add estimated avg latency to selected server
        upstream_server_status[server_id].delays.put((ts, upstream_server_status[server_id].avglatency.get()))
        r = requests.get(endpoint, headers=self.headers, timeout=self.TIME_OUT)
        # update estimated avg latency
        upstream_server_status[server_id].avglatency.put(r.json()['delays'])
        return r
      