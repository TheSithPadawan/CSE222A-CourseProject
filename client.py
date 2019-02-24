import requests
import threading
import time

PORT = '8080'
HOST = '127.0.0.1'

class Client:
    latency = list()
    init_time = time.time()

    def get_num_requests(self, t):
        return t

    def get_request_type(self):
        return 'c'

    def asyn_request(self, endpoint):
        ts = time.time()
        time_elapsed = round(ts-self.init_time, 5)
        print(threading.currentThread().getName(), "sends request at time", time_elapsed)
        r = requests.get(endpoint)
        self.latency.append((time_elapsed, round(time.time()-ts, 5)))

    def send_requests(self, duration=60):
        t = 1
        while t < duration:
            numOfRequest = self.get_num_requests(t)
            interval = 1/(numOfRequest)
            for i in range(numOfRequest):
                time.sleep(interval)
                requestType = self.get_request_type()
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