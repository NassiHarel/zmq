import sys
import time
import zmq
import gevent
import statistics
import threading
from random import randrange
from zmq.eventloop import ioloop, zmqstream
from util.encoding import Encoding
from util.decorators import timing

context = zmq.Context()
encoding = Encoding("msgpack")

diffs = []
count = 0
stats = None

def process(msg):
    global count
    global stats
    count += 1
    data = encoding.decode(msg)
    num = data["num"]
    print('receive message {num}'.format(num=num))
    sleep = randrange(10)
    # time.sleep(5)
    diffs.append(sleep)

    if(count % 10 == 0):
        median = statistics.median(diffs)
        mean = statistics.mean(diffs)
        diffs.clear() # if we don't clear, this will become very slow
        stats = {"median": median, "mean": mean, "count": count}


def setInterval(func, sec, arg):
    def func_wrapper():
        setInterval(func, sec, arg)
        func(arg)
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def sendStatistics(socketReq):
    global stats
    if(not stats):
        print('no statistics')
        return
    print('send statistics median={median}, mean={mean}, count={count}'.format(**stats))
    socketReq.send(encoding.encode(stats))
    data = socketReq.recv()


def startStatistics():
    socketReq = context.socket(zmq.REQ)
    socketReq.connect("tcp://127.0.0.1:9023")
    setInterval(sendStatistics, 2, socketReq)


@timing
def consumer():
    global count
    startStatistics()

    socketPull = context.socket(zmq.PULL)
    socketPull.setsockopt(zmq.RCVHWM, 1)
    socketPull.setsockopt(zmq.RCVBUF, 1)
    socketPull.connect("tcp://127.0.0.1:9022")

    while True:
        if(count == 100000):
            break
        msg = socketPull.recv()
        process(msg)


consumer()
