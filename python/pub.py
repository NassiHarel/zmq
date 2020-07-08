import time
import zmq
import gevent
import threading
from util.encoding import Encoding
from util.decorators import timing
from recv_statistics import startStatistics

context = zmq.Context()
msgCount = 0

def processStat():
    return msgCount

@timing
def startPublisher():
    global msgCount
    encoding = Encoding("msgpack")
    publisher = context.socket(zmq.PUB)
    # publisher.setsockopt(zmq.SNDHWM, 1)
    # publisher.setsockopt(zmq.SNDBUF, 2)
    publisher.bind("tcp://*:9022")
    bigBytes = 1 # bytearray(b'\xdd'*(1024*1024))
    startStatistics(processStat)

    while True:
        if(msgCount == 100000):
            break
        
        msgCount += 1
        message = encoding.encode({'num': msgCount, "object": {"data": True}, "bigBytes": bigBytes} )
        publisher.send(message, 120)
        print('sent message {count}'.format(count=msgCount))


startPublisher()
