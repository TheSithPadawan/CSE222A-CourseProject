import requests
import threading
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn

"""
main program:
main thread: accept connection 
when a connection is accepted, use thread
to do the work:
    copy each http request
    forward to upstream server in a roundrobin fashion 
"""

connection_count = 0
upstream_server = {
    0: "http://127.0.0.1:5000",
    1: "http://127.0.0.1:5000"
    }

class Handler(BaseHTTPRequestHandler):
   
    def do_GET(self):
        global connection_count
        print (threading.currentThread().getName(), "get the request, ready to serve")
        connection_count += 1
        num_server = len(upstream_server)
        server_id = connection_count % num_server
        addr = upstream_server[server_id]+self.path
        # post the request
        r = requests.get(addr, headers=self.headers)
        self.send_response(r.status_code)
        self.end_headers()
        self.wfile.write(bytes(r.text, 'UTF-8'))
        return

class LoadBalancer(ThreadingMixIn, HTTPServer):
    """
    Handles requests in a separate thread.
    """
    

if __name__ == "__main__":
    lb = LoadBalancer(('localhost', 8080), Handler)
    lb.serve_forever()            
            
