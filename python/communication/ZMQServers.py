import signal
import sys
import threading
from gevent import sleep
import zmq.green as zmq
from .ZMQServer import ZMQServer
context = zmq.Context()




class ZMQServers(object):
    def __init__(self, port, replyFunc):
        self._isServing = False
        self._active = True
        self._replyFunc = replyFunc
        self._url_worker = "inproc://workers"
        self._url_client = "tcp://*:" + str(port)
        self._instances = []
        signal.signal(signal.SIGINT, self.signal_handler)

    def listen(self):
        self.clients = context.socket(zmq.ROUTER)
        self.clients.bind(self._url_client)

        self.workers = context.socket(zmq.DEALER)
        self.workers.bind(self._url_worker)

        for i in range(0, 5):
            server = ZMQServer(context, self._replyFunc, self._url_worker)
            server.start()
            self._instances.append(server)

        zmq.device(zmq.QUEUE, self.clients, self.workers)

        clients.close()
        workers.close()
        context.term()

    def shutDown(self):
        self.stop()
        self.clients.close()
        self.workers.close()
        context.term()

    def isServing(self):
        res = all(i.isServing() for i in self._instances)
        return res

    def stop(self):
        for i in self._instances:
            i.stop()
            i.close()
            i.join(timeout=1)

    def close(self):
        for i in self._instances:
            i.close()
    
    def signal_handler(self, sig, frame):
        print('You pressed Ctrl+C!')
        self.shutDown()
        sys.exit(0)
    
   

   
