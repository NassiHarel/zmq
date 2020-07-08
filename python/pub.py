import time
import zmq
import gevent
import threading
from util.encoding import Encoding
from util.decorators import timing
from recv_statistics import processStat

context = zmq.Context()


@timing
def startPublisher():
    msgCount = 0
    encoding = Encoding("msgpack")
    publisher = context.socket(zmq.PUB)
    # publisher.setsockopt(zmq.SNDHWM, 1)
    # publisher.setsockopt(zmq.SNDBUF, 2)
    publisher.bind("tcp://*:9022")
    bigBytes = bytearray(b'\xdd'*(1024*1024))

    while True:
        if(msgCount == 10000):
            break
        
        msgCount += 1
        message = encoding.encode({'num': msgCount, "object": {"data": True}, "bigBytes": bigBytes} )
        publisher.send(message, 120)
        print('sent message {count}'.format(count=msgCount))


startPublisher()
