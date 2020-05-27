import zmq
from util.decorators import timing
from util.encoding import Encoding
context = zmq.Context()

class DataRequest:

    def __init__(self, reqDetails):
        self.poller = zmq.Poller()
        self.socket = context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.setsockopt(zmq.RCVTIMEO, 1000)
        self.socket.connect('tcp://'+reqDetails['host']+':'+str(reqDetails['port']))
        self.poller.register(self.socket, zmq.POLLIN)


    @timing
    def invoke(self):
        try:
            self.socket.send(b'hello')
            print ('client: send message to server')
            message = self.socket.recv()
            ex = self.poller.poll(5000)
            if ex:
                message = self.socket.recv()
            else:
                raise IOError("Timeout processing auth request")
        
            self.socket.close()

        except Exception as e:
             print (e)
       

    def close(self):
        self.socket.close()
