#!/bin/sh
# make vegeta call

########
PORT=8080
HOST="127.0.0.1"
RATE=10
DURATION="30s"
########

if [ $# -eq 0 ]
then
  echo "=== SENDING REQUESTS TO SERVER http://${HOST}:${PORT} FOR ${DURATION}"
  echo "GET http://${HOST}:${PORT}/foo?type=b" | vegeta attack -name=50qps -rate=$RATE -duration=$DURATION > results.bin
  echo "=== PLOTTING"
  cat results.bin | vegeta plot > plot.html
  cat results.bin | vegeta report -type=text > report.txt
  open plot.html
  open report.txt
  echo "=== DONE"
else
  # any parameter passed in will call live plot
  echo "GET http://${HOST}:${PORT}" | \
      vegeta attack -rate $RATE -duration $DURATION | vegeta encode | \
      jaggr @count=rps \
            hist\[100,200,300,400,500\]:code \
            p25,p50,p95:latency \
            sum:bytes_in \
            sum:bytes_out | \
      jplot rps+code.hist.100+code.hist.200+code.hist.300+code.hist.400+code.hist.500 \
            latency.p95+latency.p50+latency.p25 \
            bytes_in.sum+bytes_out.sum
fi