import zmq.green as zmq
from gevent import spawn
import threading
from util.decorators import timing
context = zmq.Context()


class DataServer(object):
    def __init__(self, reply):
        self.reply = reply

    def listen(self, port):
        self._socket = context.socket(zmq.REP)
        self._socket.bind("tcp://*:" + str(port))
        print ('server: listen on port 9020')

        while True:
            message = self._socket.recv()
            print ('server: got message from client, sending...')
            self.send()
    
           
    @timing
    def send(self):
        res =  self._socket.send(self.reply(), copy=False, track=True)
        print(res) # copy add 2200ms
