

**Server:**

​	Listen for connection from load balancer and handle different requests with artificial delays (computation, io, etc)

**Client:**

​	Send requests to load balancer in a specific pattern

**LoadBalancer:**

1. Take incoming request from clients, redirect requests to servers based on load balancing algorithms
2. Keep records of all servers, and be able to handle server failure, optimize request response time, and reduce connection overflows(errors).

**Matrix:**

1. Average response time (request delay), CDF
2. Number of connection aborted



**TODOs**:

1. Monitor server side cpu load with respect to request latency, (Python CPU load should be high when latency is high) **@Saurabh  Goyal @Jingwu Xu**
2. Design different server load pattern for dummy workers (sin, cos, periodical) **@Rongrong Miao**
3. Think over more Load Balancing measurement matrix **@ALL**
4. Simulate network level constrains for load balancer, e.g. maximum connection limit, time out, server failure, and its implementation **@ALL**

**Meetings:**

1. **2/17  6:30 pm.** @Biomedical Library Building (BLB) Room 107


Week 4 specifications : 



**ToDO's for Week starting 18 Feb:** 

Long term view : 
1) Implementing our Load Balancing Algorithm
2) Implementing Server Failure 
3) Implementing Maximum Connection check 
4) Caching the popular requests on the LB 

This week 
1) Designing different types of requests following normal distribution. - Assigned to Rongrong Miao


2) Implementing a basic health check pinging the server periodically - Assigned to Saurabh Goyal 


3) Modifying the server in a way to serve the heath check requests - Assigned to Jingwu 


4) Report Work - Assigned to Jingwu ( to be reviewed and edited by Rongrong Miao)

Midweek Review : 
Thursday 9.00 PM

Weekly meeting - 
TBD

Future Extensions : 
1) Sending back "bandwith" as the health check response