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
    # time.sleep(0.005)
    processStat()


@timing
def startSubscriber():
    msgCount = 0
    startStatistics()
    subscriber = context.socket(zmq.SUB)
    # subscriber.setsockopt(zmq.SUBSCRIBE, b"B")
    # socketPull.setsockopt(zmq.RCVHWM, 1)
    # socketPull.setsockopt(zmq.RCVBUF, 2)
    subscriber.subscribe("")
    subscriber.connect("tcp://127.0.0.1:9022")

    while True:
        if(msgCount == 10000):
            break

        msgCount += 1
        msg = subscriber.recv()
        process(msg)


startSubscriber()
