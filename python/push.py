import time
import zmq
from util.encoding import Encoding
from util.decorators import timing
from recv_statistics import startStatistics
context = zmq.Context()

msgCount = 0

def processStat():
    return msgCount

@timing
def producer():
    global msgCount
    encoding = Encoding("msgpack")
    socketPush = context.socket(zmq.PUSH)
    # socketPush.setsockopt(zmq.SNDHWM, 1)
    # socketPush.setsockopt(zmq.SNDBUF, 2)
    socketPush.bind("tcp://*:9022")
    bigBytes = 1 # bytearray(b'\xdd'*(1024*1024))
    startStatistics(processStat)
    
    while True:
        if(msgCount == 100000):
            break
        
        msgCount += 1
        message = encoding.encode({'num': msgCount, "object": {"data": True}, "bigBytes": bigBytes} )
        socketPush.send(message, copy=False)
        print('sent message {count}'.format(count=msgCount))


producer()
