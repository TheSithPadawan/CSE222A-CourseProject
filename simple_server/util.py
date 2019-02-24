import numpy as np
import time
import matplotlib.pyplot as plt 

class MaxQueue():
    def __init__(self, size=5):
        self.size = size
        self.data = [0] * size
        self.pointer = 0

    def put(self, item):
        self.data[self.pointer] = item
        self.pointer += 1
        self.pointer %= self.size

    def get(self):
        return self.data[self.pointer]

    def __str__(self):
        return str(self.data)

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
    def get_traffic_pattern(self, t, A = 50, T = 60):
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
        

if __name__ == "__main__":
    # sample usage
    obj = RequestUtil(False)
    print ("-------testing for getting traffic pattern-------")
    print (obj.get_traffic_pattern(0))
    print (obj.get_traffic_pattern(30))
    print (obj.get_traffic_pattern(45))

    print ("-------testing for processing request-------")
    obj.process_request(10)
    obj.process_request(100)

    # try draw 20 samples from distribution
    print ("-------testing for drawing samples-------")
    for i in range(20):
        print (obj.draw_sample())
