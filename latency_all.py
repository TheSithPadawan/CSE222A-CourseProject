import numpy as np
import pylab as plt


total_bins = 400
# Sample data


fig = plt.figure()
ax = fig.add_subplot(111)  
ax.spines['top'].set_color('none')
ax.spines['bottom'].set_color('none')
ax.spines['left'].set_color('none')
ax.spines['right'].set_color('none')
ax.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')

ax.set_xlabel('Time')
ax.set_ylabel('Average Response Time')

plt1 = fig.add_subplot(511) 
plt2 = fig.add_subplot(512) 
plt3 = fig.add_subplot(513) 
plt4 = fig.add_subplot(514) 
plt5 = fig.add_subplot(515) 



X = [] 
Y = [] 
f = open("ch_latency (1).txt","r")
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

# plt.scatter(X,Y,color='k',alpha=.2,s=2)
plt1.plot(bins-delta/2,running_mean, label = 'Chained Round Robin')
# plt.axis('tight')
plt1.axes.get_xaxis().set_visible(False)

plt1.spines['top'].set_visible(False)
plt1.spines['right'].set_visible(False)
# plt1.spines['bottom'].set_visible(False)



# Sample data
X = [] 
Y = [] 
f = open("rr_latency (1).txt","r")
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

# plt.scatter(X,Y,color='k',alpha=.2,s=2)
plt2.plot(bins-delta/2,running_mean, label = 'Round Robin')
# plt.axis('tight')

plt2.axes.get_xaxis().set_visible(False)

plt2.spines['top'].set_visible(False)
plt2.spines['right'].set_visible(False)
# plt2.spines['bottom'].set_visible(False)




# Sample data
X = [] 
Y = [] 
f = open("ra_latency (1).txt","r")
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

# plt.scatter(X,Y,color='k',alpha=.2,s=2)
plt3.plot(bins-delta/2,running_mean, label = 'Random')
# plt.axis('tight')
plt3.axes.get_xaxis().set_visible(False)

plt3.spines['top'].set_visible(False)
plt3.spines['right'].set_visible(False)
# plt3.spines['bottom'].set_visible(False)






# Sample data
X = [] 
Y = [] 
f = open("ll_latency (1).txt","r")
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

# plt.scatter(X,Y,color='k',alpha=.2,s=2)
plt4.plot(bins-delta/2,running_mean, label = 'Least Latency')
# plt4.axis('tight')

plt4.axes.get_xaxis().set_visible(False)

plt4.spines['top'].set_visible(False)
plt4.spines['right'].set_visible(False)
# plt4.spines['bottom'].set_visible(False)




# Sample data
X = [] 
Y = [] 
f = open("lc_latency (1).txt","r")
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

# plt.scatter(X,Y,color='k',alpha=.2,s=2)
plt5.plot(bins-delta/2,running_mean, label = 'Least Connection')
# plt.axis('tight')


# plt1.axes.get_xaxis().set_visible(False)

plt5.spines['top'].set_visible(False)
plt5.spines['right'].set_visible(False)
# plt1.spines['bottom'].set_visible(False)








plt1.set_ylim(0,4)
plt2.set_ylim(0,4)
plt3.set_ylim(0,4)
plt4.set_ylim(0,4)
plt5.set_ylim(0,4)







plt1.legend(loc='upper right')
plt2.legend(loc='upper right')
plt3.legend(loc='upper right')
plt4.legend(loc='upper right')
plt5.legend(loc='upper right')





plt.show()