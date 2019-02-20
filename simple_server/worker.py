import os 
import time
import psutil             
import matplotlib.pyplot as plt
from queue import Queue
from threading import Thread
import random
import numpy as np 

class QueryWorker(Thread):

    def __init__(self, queue, delays, start_time):
        Thread.__init__(self)
        self.queue = queue
        self.delays = delays
        self.start_time = start_time

    def run(self):
        print('query worker run at 0 s')
        while True:
            # Get the work from the queue and expand the tuple
            http_obj = self.queue.get()
            try:
                ts = time.time()
                delay_time = 0
                if http_obj.body['type'] == 'a':
                    delay_time = self.dummy_job(3)
                elif http_obj.body['type']== 'b':
                    delay_time = self.dummy_job(6)
                else:
                    delay_time = self.dummy_job(2)
                # print(http_obj)
                print('worker delays', delay_time)
                # http_obj.respond({'delays': delay_time})
                self.delays.append((ts-self.start_time, delay_time))
            finally:
                self.queue.task_done()

    """
    length varies for different type
    total latency = base latency * random in range [0.85 - 1.51)
    """
    def dummy_job(self, length):
        ts = time.time()
        # modify here to adjust run time
        base = 10**6*length
        actual = int(base * np.random.uniform(0.85, 1.51))
        for i in range(actual):
            a = 1
        return time.time()-ts

class DummyWorker(Thread):
    def __init__(self, start_delay, TTL):
        Thread.__init__(self)
        self.start_delay = start_delay
        self.TTL = TTL
        
    def run(self):
        time.sleep(5)
        print('dummy worker run at', 5, 's')
        start_time = time.time()
        flag = True
        last_sleep = time.time()
        while time.time() - start_time < self.TTL:
            x = 1
            if time.time()-last_sleep > 5:
                # continuesly working for 5s
                # sleep for 5s
                time.sleep(5)
                last_sleep = time.time()
                
class MonitorWorker(Thread):

    def __init__(self, time_span):
        Thread.__init__(self)
        self.time_span = time_span

    def run(self):
        X=[]
        Y=[]

        for i in range(self.time_span*100):
            X.append(i*0.01)
            Y.append(psutil.cpu_percent())
        plt.figure(figsize=(12,6))
        plt.scatter(X,Y) 
        plt.xlabel('Time') 
        plt.ylabel('CPU Usage Percentage') 
        plt.show() 
