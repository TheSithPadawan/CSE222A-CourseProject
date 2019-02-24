class MaxQueue():
    def __init__(self, size=5):
        self.size = size
        self.data = [0] * size
        self.pointer = 0

    def put(self, item):
        self.data[self.pointer] = item
        self.pointer += 1
        self.pointer %= self.size

    def get(self):
        return self.data[self.pointer]

    def __str__(self):
        return str(self.data)

class ServerStatus():
    def __init__(self):
        self.workloads = 0
        self.delays = MaxQueue(5)
        self.alive = True

upstream_server = {
    0: "http://127.0.0.1:5050",
    1: "http://127.0.0.1:6000"
    }

upstream_server_status = {
    0: ServerStatus(),
    1: ServerStatus()
}