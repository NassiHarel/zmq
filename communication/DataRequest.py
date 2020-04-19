import zmq
from util.decorators import timing
context = zmq.Context()

class DataRequest:

    def __init__(self, reqDetails):
        self.socket = context.socket(zmq.REQ)
        self.socket.connect('tcp://'+reqDetails['host']+':'+str(reqDetails['port']))
        print ('client: connected to server')

    @timing
    def invoke(self):
        self.socket.send(b'hello')
        message = self.socket.recv(copy=False)
        return message
