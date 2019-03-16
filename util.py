import time
import numpy as np
import matplotlib.pyplot as plt

LOCAL = False

def get_timestamp(entity):
    timestamp =  str(time.strftime("[%D %H:%M:%S]", time.localtime(time.time())))
    return '%s - - %-15s' % (timestamp, entity+':')

class Queue():
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

class AvgLatency():
    def __init__(self):
        self.latency = []

    def put(self, latency):
        self.latency.append(latency)

    def get(self):
        # return sum(self.latency.data)/self.latency.size
        return self.exp_Avg(np.array(self.latency), len(self.latency))

    def exp_Avg(self, data, window):
        weights = np.exp(np.linspace(-1., 0., window))
        weights /= weights.sum()
        return np.sum(data * weights)

class ServerStatus():
    def __init__(self):
        self.workloads = 0
        self.delays = Queue(5)
        self.alive = True
        self.avglatency = AvgLatency()

if LOCAL:
    upstream_server = {
        0: "http://0.0.0.0:5050",
        1: "http://0.0.0.0:6000"
        }

    upstream_server_status = {
        0: ServerStatus(),
        1: ServerStatus()
    }
else:
    upstream_server = {
        0: "http://155.98.36.130:50505",
        1: "http://155.98.36.129:50505",
        2: "http://155.98.36.131:50505"
        }

    upstream_server_status = {
        0: ServerStatus(),
        1: ServerStatus(),
        2: ServerStatus()
    }

class PlotUtil():
    """
    This class helps 
    with visualization 
    of the data
    """

    """
    input: the latency file 
    output: latency -- converts to ms 
    """
    def read_from_file(self, fn):
        latency=[]
        with open(fn,'r') as f:
            for line in f:
                data = line.strip().split()
                latency.append(float(data[1]))
        # convert seconds to ms 
        return np.array(latency) * 1000

    """
    input: list format -- [(latency array, algorithm label)]
    output: cdf graph saved at local directory 
    """
    def get_cdf(self, arr):
        fig, ax = plt.subplots(1, 1)
        n_bins = 100
        colors = ['r', 'g', 'b', 'y', 'c', 'm']
        for i in range(len(arr)):
            data=arr[i][0]
            counts, bin_edges = np.histogram(data, bins=n_bins, normed=True)
            cdf = np.cumsum(counts)
            # n, bins, patches = ax.hist(data, n_bins, normed=1, histtype='stepfilled', cumulative=True, label=arr[i][1], color=colors[i])
            ax.plot(bin_edges[1:], cdf/cdf[-1], label=arr[i][1], color=colors[i])
            print ('statistics for algorithm', arr[i][1])
            for q in [50, 90, 95, 100]:
                print ("{} percentile: {}".format (q, np.percentile(data, q)))

        ax.grid(True)
        ax.set_title('CDF for Load Balancing Algorithms')
        ax.set_xlabel('response latency (ms)')
        ax.set_ylabel('probability')
        ax.legend()
        plt.savefig('cdf_output.png')

    def get_histogram(self, arr):
        num_bins = 100
        fig, ax = plt.subplots(1, 1)
        n, bins, patches = ax.hist(arr, num_bins, facecolor='blue', normed=1, alpha=0.5)
        ax.grid(True)
        ax.set_title('PDF for Processing Time')
        ax.set_xlabel('Server Processing Time')
        ax.set_ylabel('Probability')
        plt.savefig('time_distribution.png')

        
if __name__ == "__main__":

    """
    change file name for the latency files
    """
    plot_obj = PlotUtil()
    arr1 = plot_obj.read_from_file('rr_cpu_latency.txt') 
    arr2 = plot_obj.read_from_file('ra_cpu_latency.txt') 
    arr3 = plot_obj.read_from_file('lc_cpu_latency.txt')
    arr4 = plot_obj.read_from_file('ll_cpu_latency.txt') 
    arr5 = plot_obj.read_from_file('ch_cpu_latency.txt')
    data = [(arr1, 'round robin'),
           (arr2, 'random'),
            (arr3, 'least connection'),
            (arr4, 'latency-based'),
            (arr5, 'chained round robin')]
    plot_obj.get_cdf(data)
    

    # plotting server request processing time distribution
    """
    plot_obj = PlotUtil()
    arr = plot_obj.read_from_file('latency.txt')
    plot_obj.get_histogram(arr)
    """

    
