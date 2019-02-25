import numpy as np
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

class ServerStatus():
    def __init__(self):
        self.workloads = 0
        self.delays = MaxQueue(5)
        self.alive = True

upstream_server = {
    0: "http://127.0.0.1:5050",
    1: "http://127.0.0.1:6000"
    }

upstream_server_status = {
    0: ServerStatus(),
    1: ServerStatus()
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
        return np.array(latency) * 1000

    """
    input: list format -- [(latency array, algorithm label)]
    output: cdf graph saved at local directory 
    """
    def get_cdf(self, arr):
        fig, ax = plt.subplots(1, 1)
        n_bins = 100
        colors = ['r', 'g']
        for i in range(len(arr)):
            data=arr[i][0]
            n, bins, patches = ax.hist(data, n_bins, normed=1, histtype='step', cumulative=True, label=arr[i][1], color=colors[i])
        ax.grid(True)
        ax.set_title('CDF for Load Balancing Algorithms')
        ax.set_xlabel('response latency (ms)')
        ax.set_ylabel('probability')
        ax.legend()
        plt.savefig('cdf_output.png')
        
if __name__ == "__main__":

    """
    change file name for the latency files
    """
    plot_obj = PlotUtil()
    arr1 = plot_obj.read_from_file('rr_latency.txt')
    arr2 = plot_obj.read_from_file('random_latency.txt')

    data = [(arr1, 'round robin'), (arr2, 'random')]
    plot_obj.get_cdf(data)
    
