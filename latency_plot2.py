import numpy as np
import pylab as plt


total_bins = 400
colors =['r', 'g', 'b', 'y', 'c']
# Sample data
X = [] 
Y = [] 
f = open("ch_latency.txt","r")
while True:
	line = f.readline()
	if not line:
		break 
	line = line.split(" ")
	X.append(float(line[0]))
	Y.append(float(line[1]))

z=min(X)
X[:] = [x - z for x in X]

X=np.array(X)
Y=np.array(Y)

bins = np.linspace(X.min(),X.max(), total_bins)
delta = bins[1]-bins[0]
idx  = np.digitize(X,bins)
running_mean = [np.mean(Y[idx==k]) for k in range(total_bins)]

plt.scatter(X,Y,color='k',alpha=.2,s=2)
# plt.plot(bins-delta/2,running_mean, color=colors[4], label='Chained Round-robin')


# plt.axis('tight')
plt.title("Response Time vs Time")
plt.xlabel('Time')
plt.legend(loc='upper right')

plt.ylabel('Response Time') 

plt.show()