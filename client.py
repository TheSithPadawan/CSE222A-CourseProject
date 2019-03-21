import requests
import threading
import time
import numpy as np
from util import get_timestamp

LOCAL = False
if LOCAL:
    PORT = '8080'
    HOST = '0.0.0.0'
else:
    PORT = '50505'
    HOST = '155.98.36.127'

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
    def get_traffic_pattern(self, t, A = 200, T = 30):
        pos = t % T
        num_request = A * np.abs(np.sin((t/T) * np.pi))
        return int(num_request) + 0

    """
    draw a sample request to send from log normal distribution 
    input: mu, sigma from the original gauss distribution 
    output: label of the request to send 
    """
    def draw_sample(self, mu = 3.7, sigma = 1.):

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
            # fp.write('EOF\n')
            


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
        print(get_timestamp('Client'), "sends request at time", time_elapsed)
        try:
            r = requests.get(endpoint, timeout=8)
            self.responsecodes.append(str(r.status_code))
        except:
            print(get_timestamp('Client'), "requests error")
            self.requestfailed += 1

        self.latency.append((time_elapsed, round(time.time()-ts, 5)))
        return

    def send_requests(self):
        t = 0
        self.init_time =  time.time()
        duration = len(self.requests)
        threads = list()
        while t < duration:
            numOfRequest = self.requests[t]
            interval = 1/(len(numOfRequest)+1)
            for i in range(len(self.requests[t])):
                requestType = self.requests[t][i]
                endpoint = "http://"+HOST+":"+PORT+"/foo?type="+str(requestType)
                thread = threading.Thread(target=self.asyn_request, args = (endpoint, interval*(i+1)))
                thread.start()
                threads.append(thread)
            t += 1
            time.sleep(1)

        for thread in threads:
            thread.join()

    def save_extra(self):
        # save supplementary
        print('writing extras to file')
        with open('extra.txt', 'w') as fp:
            fp.write('requests sent:     \t'+str(self.requestsent)+'\n')
            fp.write('responses received:\t'+str(len(self.responsecodes))+'\n')
            fp.write('responses timeouts:\t'+str(sum(code == '504' for code in self.responsecodes))+'\n')
            fp.write('requests failed:   \t'+str(self.requestfailed)+'\n')
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

    client.read_request_file('requests_60s_hp.txt')
    client.send_requests()
    client.save_extra()
   
    # client.get_request_file('requests_60s_hp.txt')
