import zmq
from gevent import spawn
import threading
from util.decorators import timing
context = zmq.Context()


mb = 1024 * 1024

def create_bytearray(sizeBytes):
    return bytearray(b'\xdd'*(sizeBytes))

class DataServer(object):

    def listen(self, port):
        self._socket = context.socket(zmq.REP)
        self._socket.bind("tcp://*:" + str(port))
        self._data = create_bytearray(20)
        print ('server: listen on port 9020')
        self.serve()
    
    def serve(self):
        while True:
            message = self._socket.recv()
            print ('server: got message from client, sending...')
            self.send(self._data)

           
    @timing
    def send(self, data):
        self._socket.send(data, copy=False) # copy add 2200ms
