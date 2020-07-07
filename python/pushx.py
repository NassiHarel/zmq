import time
import zmq
import gevent
import threading
from util.encoding import Encoding
from util.decorators import timing

msgCount = 0

def recvStatistics(socketRep, encoding):

    """Receive Statistics

    receive statistics from all consumers.
    need to sum all proccessed messages by algorithm.
    then decide if need to scale up/down

    """
    
    global msgCount

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
    context = zmq.Context()
    socketPush = context.socket(zmq.PUSH)
    socketRep = context.socket(zmq.REP)
    socketPush.bind("tcp://*:9022")
    socketRep.bind("tcp://*:9023")
    encoding = Encoding("msgpack")
   
    threading.Thread(target=recvStatistics, args=(socketRep, encoding)).start()

    while True:
       
        if(msgCount == 100000):
            break
        
        msgCount += 1
        work_message = encoding.encode({'num': msgCount, "object": {"data": True}, "array": [1, 2, 3, 4, 5]})
        socketPush.send(work_message, copy=False)
        print('sent message {count}'.format(count=msgCount))



producer()
