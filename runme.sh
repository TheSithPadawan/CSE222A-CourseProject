#!/bin/sh
# make vegeta call

########
PORT=8080
HOST="127.0.0.1"
RATE=10
DURATION="30s"
########
#
if [ -z "$1" ] ; then
  echo "[ATTENTION] USING DIFFERENT TERMINALS TO RUN EACH OF THE FOLLOWING COMMANDS"
  echo "==========================================================================="
  echo "[-ss]\t: start servers on default settings"
  echo "[-lb] \t: start loadbalancer on default settings"
  echo "[-cl]\t: start client on default settings"
  echo "[-show]\t: show onrunning python processes"
  
  echo "[-kill]\t: kill all running python processes"

  echo "[-vegeta]\t: run vegeta requests flooding"
  echo "\t[-live]\t: run vegeta requests flooding live plotting"
fi

if [ "$1" == "-ss" ] ; then
  echo "[-ss]\t: start servers on default settings"
  echo "start server 1 on port 5050"
  python server.py -p 5050 &
  echo "start server 1 on port 6000"
  python server.py -p 6000 &
fi

if [ "$1" == "-lb" ] ; then
  echo "[-lb] \t: start loadbalancer on default settings"
  echo "start loadbalancer on port 8080"
  python loadbalancer.py &
fi

if [ "$1" == "-cl" ] ; then
  echo "[-cl]\t: start client on default settings"
  python client.py &
fi

if [ "$1" == "-show" ] ; then
  echo "[-show] \t: show onrunning python processes"
  ps -ef | grep python
fi

if [ "$1" == "-kill" ] ; then
  echo "[-kill] \t: kill all python onrunning processes"
  pkill -f python
fi

if [ "$1" == "-vegeta" ] ; then
  if [ -z "$2" ] ; then
    echo "=== SENDING REQUESTS TO SERVER http://${HOST}:${PORT} FOR ${DURATION}"
    echo "GET http://${HOST}:${PORT}/foo?type=b" | vegeta attack -name=50qps -rate=$RATE -duration=$DURATION > results.bin
    echo "=== PLOTTING"
    cat results.bin | vegeta plot > plot.html
    cat results.bin | vegeta report -type=text > report.txt
    open plot.html
    open report.txt
    echo "=== DONE"
  fi
  if [ "$2" == "live" ] ; then
    echo "GET http://${HOST}:${PORT}" | vegeta attack -rate $RATE -duration $DURATION | vegeta encode | \
    jaggr @count=rps \
          hist\[100,200,300,400,500\]:code \
          p25,p50,p95:latency \
          sum:bytes_in \
          sum:bytes_out | \
    jplot rps+code.hist.100+code.hist.200+code.hist.300+code.hist.400+code.hist.500 \
          latency.p95+latency.p50+latency.p25 \
          bytes_in.sum+bytes_out.sum
  fi
fi
if [ "$1" ] ; then
  echo "done"
fi
