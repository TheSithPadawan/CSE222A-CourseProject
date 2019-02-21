import numpy as np
import sys
import subprocess
import os

def generate_distribution(weights):
    cum_weight = [0] * 3
    cum_weight[0] = weights[0]
    cum_weight[1] = cum_weight[0] + weights[1]
    cum_weight[2] = cum_weight[1] + weights[2]
    requests = ['GET http://localhost:8080/foo?type=a',
                'GET http://localhost:8080/foo?type=b',
                'GET http://localhost:8080/foo?type=c']
    
    with open ("./targets.txt", 'w') as f:
        for i in range(10):
            magic_number = np.random.uniform(0, 1)
            if magic_number <= cum_weight[0]:
                f.write(requests[0])
                f.write('\n')
            elif magic_number <= cum_weight[1]:
                f.write(requests[1])
                f.write('\n')
            else:
                f.write(requests[2])
                f.write('\n')



if __name__ == "__main__":
    weights = []
    for i in range(1, 4):
        weights.append(float(sys.argv[i]))
    # generate_distribution(weights)
    os.system("vegeta attack -duration=10s -targets targets.txt -keepalive=false | tee results.bin | vegeta report")
    
