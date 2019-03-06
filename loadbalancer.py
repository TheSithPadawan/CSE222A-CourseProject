import argparse
import requests
import threading
import time
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from util import (
    upstream_server, 
    upstream_server_status,
    get_timestamp
    )
from requesthandler import (
    RandomHandler,
    RoundRobinHandler,
    LeastConnectionHandler,
    ChainedConnectionHandler,
    LeastLatencyHandler
    )

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

class LoadBalancerServer():
    HOST_NAME = '155.98.36.127'
    PORT_NUMBER = 50505
    # PORT_NUMBER = 8080
    # HOST_NAME = 'localhost'
    REQUESTHANDLER = RandomHandler  # Change Load Balancing Algorithm

    def select_handler(self, abbr=None, alls=True):
        if abbr == 'ra':
            self.REQUESTHANDLER = RandomHandler
        if abbr == 'rr':
            self.REQUESTHANDLER = RoundRobinHandler
        if abbr == 'lc':
            self.REQUESTHANDLER = LeastConnectionHandler
        if abbr == 'ch':
            self.REQUESTHANDLER = ChainedConnectionHandler
        if abbr == 'll':
            self.REQUESTHANDLER = LeastLatencyHandler
        print(get_timestamp('LoadBalancerServer'), 'uses', str(self.REQUESTHANDLER.__name__))


    def start_server(self, HOST_NAME=None):
        if HOST_NAME == None:
            HOST_NAME = self.HOST_NAME
        PORT_NUMBER = self.PORT_NUMBER
        httpd = ThreadingSimpleServer((HOST_NAME, PORT_NUMBER), self.REQUESTHANDLER)
        try:
            httpd.serve_forever()
        except:
            print('Server Closed')
            httpd.server_close()

    def start_healthcheck(self):
        endpoints = [(key, ip+'/foo?type=hc') for (key, ip) in upstream_server.items()]
        for serverID, endpoint in endpoints:
            print(endpoint)
            thread = threading.Thread(target=self.get_server_status, args = (endpoint, serverID))
            thread.start()
        threading.Thread(target=self.get_num_servers, args = (3,)).start()
        
    def get_num_servers(self, period=3):
        while True:
            time.sleep(period)
            alives = 0
            for serverID in upstream_server_status.keys():
                if upstream_server_status[serverID].alive ==True:
                    alives += 1
            print(get_timestamp('LoadBalancerServer'), alives, 'servers alive')

    def get_server_status(self, endpoint, serverID, frequency=0.1):
        z=0
        cnt = 0
        failure_threshold = 3
        # while upstream_server_status[serverID].alive:
        while True:
            if upstream_server_status[serverID].alive:
                time.sleep(frequency)
            else:
                time.sleep(frequency*10)

            ts = time.time()
            cnt += 1
            try:
                requests.get(endpoint)
                z=0 # reset if there is a reponse
            except:
                z+=1
                if z<=failure_threshold*10:
                    continue
                upstream_server_status[serverID].alive = False 
            
            delay = time.time() - ts
            upstream_server_status[serverID].delays.put((round(frequency*cnt,1),delay))
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start LoadBalancerServer listening to HTTP requests')
    parser.add_argument('-hs', '--hostname', action='store', dest='hostname', required=True, help='the host that server binds to', type=str)
    parser.add_argument('-hd', '--handler', action='store', dest='handler', help='the load balancing algorithm', type=str)
    args = vars(parser.parse_args())

    lb = LoadBalancerServer()
    lb.start_healthcheck()
    lb.select_handler(abbr=args['handler'])
    lb.start_server(args['hostname'])    
            
