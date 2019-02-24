import time
from threading import Thread
import random
import numpy as np 

class DummyWorker(Thread):
    def __init__(self, start_delay, work_duration=5, sleep_duration=5, TTL=1000):
        Thread.__init__(self)
        self.start_delay = start_delay
        self.work_duration = work_duration
        self.sleep_duration = sleep_duration
        self.TTL = TTL
        
    def run(self):
        time.sleep(self.start_delay)
        print('dummy worker run at', self.start_delay, 's')
        start_time = time.time()
        flag = True
        last_sleep = time.time()
        while time.time() - start_time < self.TTL:
            x = 1
            if time.time()-last_sleep > self.work_duration:
                # continuesly working for 5s
                # sleep for 5s
                time.sleep(self.sleep_duration)
                last_sleep = time.time()