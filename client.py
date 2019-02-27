import requests
import threading
import time
import numpy as np
import matplotlib.pyplot as plt 

PORT = '8080'
HOST = '127.0.0.1'

class RequestUtil():
    """
    This class is the utility 
    class for creating request
    processing time, request distribution
    and traffic pattern 
    """
    debug = False

    def __init__(self, debug_mode):
        self.debug = debug_mode

    """
    default traffic pattern: y = A|sin(x)|
    T = 60s (one period)
    A = 50 RPS (amplitude)
    t: current time, measured by second 
    """
    def get_traffic_pattern(self, t, A = 30, T = 60):
        pos = t % T
        num_request = A * np.abs(np.sin((t/T) * np.pi))
        return int(num_request)
        # return 1

    """
    draw a sample request to send from log normal distribution 
    input: mu, sigma from the original gauss distribution 
    output: label of the request to send 
    """
    def draw_sample(self, mu = 3.4, sigma = 1.):

        s = np.random.lognormal(mu, sigma)
        
        if self.debug:
            dist = np.random.lognormal(mu, sigma, 1000)
            count, bins, ignored = plt.hist(s, 100, align='mid')
            x = np.linspace(min(bins), max(bins), 10000)
            pdf = (np.exp(-(np.log(x) - mu)**2 / (2 * sigma**2))/(x*sigma*np.sqrt(2*np.pi)))
            plt.plot(x, pdf, linewidth=2, color='r')
            plt.show()
        return int(s)
        
    """
    process each request given the parameter 
    this grows in polynomial time
    """
    def process_request(self, x):
        base = 3*x**3 + 2*x**2 + x + 10**5
        variation = np.random.uniform(0.8, 1.51)
        final = int(base * variation)
        dummy = 0
        start_time = time.time()
        for i in range(final):
            dummy += 1
        end_time = time.time()
        if self.debug:
            print ('current request with param', x, 'has been processed for', end_time - start_time,'seconds')

    """
    input: generate a request file for sending requests for
    t seconds 
    """
    def generate_request_file(self, fn, t):
        cnt = 1
        with open(fn, 'w') as fp:
            while cnt < t:
                num_request = self.get_traffic_pattern(cnt)
                line = ""
                for i in range(num_request):
                    request_type = self.draw_sample()
                    line += str(request_type) + " "
                cnt += 1
                fp.write(line)
                fp.write('\n')
            


class Client:
    init_time = 0
    requestsent = 0
    requestfailed = 0
    latency = list()
    requests = list()
    responsecodes = list()
    requestUtil = RequestUtil(False)
    
    def asyn_request(self, endpoint, delay_send=0):
        time.sleep(delay_send)
        ts = time.time()
        self.requestsent += 1
        time_elapsed = round(ts-self.init_time, 5)
        print(threading.currentThread().getName(), "sends request at time", time_elapsed)
        try:
            r = requests.get(endpoint)
            self.responsecodes.append(str(r.status_code))
        except requests.exceptions.ConnectionError:
            self.requestfailed += 1
            return

        self.latency.append((time_elapsed, round(time.time()-ts, 5)))
        return

    def send_requests(self):
        t = 0
        self.init_time =  time.time()
        duration = len(self.requests)
        while t < duration:
            numOfRequest = self.requests[t]
            interval = 1/(len(numOfRequest)+1)
            for i in range(len(self.requests[t])):
                requestType = self.requests[t][i]
                endpoint = "http://"+HOST+":"+PORT+"/foo?type="+str(requestType)
                thread = threading.Thread(target=self.asyn_request, args = (endpoint, interval*(i+1)))
                thread.start()
            t += 1
            time.sleep(1)

    def save_latency(self):
        with open('latency.txt', 'w') as fp:
            fp.write('\n'.join('%s %s' % x for x in self.latency))

    def save_extra(self):
        # save supplementary
        with open('extra.txt', 'w') as fp:
            fp.write(str(self.requestsent)+','+str(self.requestfailed))
            fp.write('\n')
            fp.write(' '.join(self.responsecodes))


    def get_request_file(self, fn, period=60):
        self.requestUtil.generate_request_file(fn, period)

    def read_request_file(self, fn):
        self.requests = []
        with open(fn, 'r') as fp:
            for line in fp:
                line = line.strip().split()
                self.requests.append(line)
            
if __name__ == "__main__":
    client = Client()
    client.read_request_file('requests.txt')
    client.send_requests()
    client.save_latency()
    client.save_extra()
    # client.get_request_file('requests.txt')
