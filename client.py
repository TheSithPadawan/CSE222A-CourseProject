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
    def get_traffic_pattern(self, t, A = 20, T = 60):
        pos = t % T
        num_request = A * np.abs(np.sin((t/T) * np.pi))
        return int(num_request)

    """
    draw a sample request to send from log normal distribution 
    input: mu, sigma from the original gauss distribution 
    output: label of the request to send 
    """
    def draw_sample(self, mu = 3.4, sigma = 1.):
        s = np.random.lognormal(mu, sigma)
        if s >= 100:
            s = 100

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
        


class Client:
    latency = list()
    init_time = time.time()
    requestUtil = RequestUtil(False)

    # def get_num_requests(self, t):
    #     return t

    # def get_request_type(self):
    #     return 'c'

    def asyn_request(self, endpoint):
        ts = time.time()
        time_elapsed = round(ts-self.init_time, 5)
        print(threading.currentThread().getName(), "sends request at time", time_elapsed)
        r = requests.get(endpoint)
        self.latency.append((time_elapsed, round(time.time()-ts, 5)))

    def send_requests(self, duration=60):
        t = 1
        while t < duration:
            numOfRequest = self.requestUtil.get_traffic_pattern(t)
            interval = 1/(numOfRequest)
            for i in range(numOfRequest):
                time.sleep(interval)
                requestType = self.requestUtil.draw_sample()
                endpoint = "http://"+HOST+":"+PORT+"/foo?type="+str(requestType)
                thread = threading.Thread(target=self.asyn_request, args = (endpoint,))
                thread.start()
            t += 1

    def save_latency(self):
        with open('latency.txt', 'w') as fp:
            fp.write('\n'.join('%s %s' % x for x in self.latency))
            
if __name__ == "__main__":
    client = Client()
    client.send_requests()
    client.save_latency()