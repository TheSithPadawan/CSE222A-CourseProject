import random
import requests
import threading
import time
from abc import ABC, abstractmethod
from http.server import BaseHTTPRequestHandler
from util import (
    upstream_server, 
    upstream_server_status,
    get_timestamp,
    AvgLatency
    )
from requests.exceptions import (
    ConnectionError,
    ConnectTimeout,
    ReadTimeout,
    Timeout
    )
import numpy as np

init_time = time.time()

class RequestHandler(BaseHTTPRequestHandler, ABC):
    connection_count = 0
    TIME_OUT = 4
    
    def do_GET(self):
        ts = time.time()
        time_elapsed = round(ts-init_time, 5)
        
        # redirect requests
        delay = self.handle_one()

        # [TODO] starts a new thread write to file?  ~0.0003s
        with open('latency.txt', 'a') as fp:
            fp.write('%s %s' % (time_elapsed, delay))
            fp.write('\n')
            fp.flush()
        return
        
    def handle_one(self):
        ts = time.time()
        RequestHandler.connection_count += 1
        self.num_server = len(upstream_server)
        
        while self.TIME_OUT > 0:
            try:
                # select next server based on different implementation
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
                # when there is an connection error resend request
                print(get_timestamp('RequestHandler'))
                print(e, end='\n\n')
                print('Exception, Retransmission required')

            self.TIME_OUT -= time.time()-ts
        
        delay = round(time.time()-ts, 5)

        print(get_timestamp('RequestHandler'), 'Sends back 504')
        self.send_response(504)
        self.end_headers()
        return delay

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
    Our own design: load balance based on expected latency per server
    - Expected latency is estimated using exponential averaging over history latency (1)
    - Exp latency per request = base_latency (1) + failure penalty (4ms in our setting) * (1/s - 1)
    s is the success rate and 1/s is the expected number of tries to get a 200 status code 
    - We maintain the number of outstanding requests at time t
    - Total expected latency per server = Exp latency per request * num_outstanding request
    - Convert the previous number to weight and implements an incremental update per request sent 
    """
    server_weights = [1/len(upstream_server)]*len(upstream_server)
    
    def redirect_server_id(self):
        # adjust for server weight 
        for serverID in upstream_server_status.keys():
            if upstream_server_status[serverID].alive == False:
                self.server_weights[serverID] = 0
        elements = [i for i in range(len(upstream_server))]
        self.reweight()
        w = np.array(self.server_weights)
        selected = np.random.choice(elements, p=w)
        return selected
    
    # adjust the server weight based on historic data 
    def reweight(self):
        num_server = len(upstream_server)
        exp_latency = [0]*num_server
        for i in range(num_server):
            # get the expected latency per server 
            latency_base = upstream_server_status[i].avglatency.get()
            # multiply by current number of outstanding requests
            # take into account of success rate and failure latency -- which is 4 ms in our case
            if upstream_server_status[i].num_reqs > 0:
                s = upstream_server_status[i].success_reqs/upstream_server_status[i].num_reqs
            else:
                s = 1
            fail_latency = 0.4 * (1/s - 1)
            exp_latency[i] = (latency_base + fail_latency) * upstream_server_status[i].workloads
            if exp_latency[i] > 0:
                self.server_weights[i] = 1/exp_latency[i]
            else:
                self.server_weights[i] = 1
        # calibrate the probabilities 
        total = sum(self.server_weights)
        for i in range(num_server):
            self.server_weights[i] = self.server_weights[i]/total
        
    def redirect_request(self, server_id, endpoint):
        t0 = time.time()
        upstream_server_status[server_id].workloads += 1
        upstream_server_status[server_id].num_reqs += 1
        r = requests.get(endpoint, headers=self.headers, timeout=self.TIME_OUT)
        upstream_server_status[server_id].workloads -= 1
        if r.status_code == 200:
            upstream_server_status[server_id].success_reqs += 1
        t1 = time.time()
        delta = t1 - t0
        upstream_server_status[server_id].avglatency.put(delta)
        return r


        
    
