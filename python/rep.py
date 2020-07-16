
import zmq
import threading
from util.encoding import Encoding
from util.decorators import timing

context = zmq.Context()
encoding = Encoding("msgpack")
socketRep = context.socket(zmq.REP)
socketRep.bind("tcp://*:5555")

bigBytes = 1 # bytearray(b'\xdd'*(1024*1024))
count = 0

@timing
def producer():
    global count
    while True:
        if(count == 100000):
            break
            
        count += 1
        msg = socketRep.recv()
        # stats = encoding.decode(msg)
        # count = stats["count"]
        message = encoding.encode({"object": {"data": True}, "bigBytes": bigBytes})
        socketRep.send(message)
        print('receive message {count}'.format(count=count))


producer()