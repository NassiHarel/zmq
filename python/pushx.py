import time
import zmq
import gevent
import threading
from util.encoding import Encoding
from util.decorators import timing

context = zmq.Context()
msgCount = 0
encoding = Encoding("msgpack")

def recvStatistics():

    """Receive Statistics

    receive statistics from all consumers.
    need to sum all proccessed messages by algorithm.
    then decide if need to scale up/down

    """
    
    global msgCount

    socketRep = context.socket(zmq.REP)
    socketRep.bind("tcp://*:9023")

    while True:
        msg = socketRep.recv()
        stats = encoding.decode(msg)
        count = stats["count"]
        percentage = "{:.2%}".format(count / msgCount)
        print('receive statistics median={median}, mean={mean}, count={count}'.format(**stats))
        print('total handled={count}/{msgCount}, ({percentage})'.format(count=count, msgCount=msgCount, percentage=percentage))
        socketRep.send(b'OK')

@timing
def producer():
    global msgCount
    
    socketPush = context.socket(zmq.PUSH)
    # socketPush.setsockopt(zmq.SNDHWM, 1)
    socketPush.setsockopt(zmq.SNDBUF, 2)
    socketPush.bind("tcp://*:9022")
   
    threading.Thread(target=recvStatistics).start()
    bigBytes = bytearray(b'\xdd'*(1024*1024))

    while True:
       
        if(msgCount == 10000):
            break
        
        msgCount += 1
        message = encoding.encode({'num': msgCount, "object": {"data": True}, "bigBytes": bigBytes} )
        socketPush.send(message, copy=False)
        print('sent message {count}'.format(count=msgCount))


producer()
