import sys
import time
import zmq
import gevent
from util.encoding import Encoding
from util.decorators import timing
from send_statistics import processStat, startStatistics

context = zmq.Context()
encoding = Encoding("msgpack")

def process(msg):
    data = encoding.decode(msg)
    num = data["num"]
    print('receive message {num}'.format(num=num))
    time.sleep(0.1)
    processStat()


@timing
def consumer():
    msgCount = 0
    
    socketPull = context.socket(zmq.PULL)
    # socketPull.setsockopt(zmq.RCVHWM, 1)
    # socketPull.setsockopt(zmq.RCVBUF, 2)
    socketPull.connect("tcp://127.0.0.1:9022")
    startStatistics()

    while True:
        if(msgCount == 100000):
            break

        msg = socketPull.recv()
        process(msg)


consumer()
