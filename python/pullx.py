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

encoding = Encoding("msgpack")
context = zmq.Context()
socketPull = context.socket(zmq.PULL)
socketReq = context.socket(zmq.REQ)
socketPull.connect("tcp://127.0.0.1:9022")
socketReq.connect("tcp://127.0.0.1:9023")
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
    time.sleep(0.5)
    diffs.append(sleep)

    if(count % 10 == 0):
        median = statistics.median(diffs)
        mean = statistics.mean(diffs)
        diffs.clear() # if we don't clear, this will become very slow
        stats = {"median": median, "mean": mean, "count": count}


def setInterval(func, sec):
    def func_wrapper():
        setInterval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def sendStatistics():
    global stats
    if(not stats):
        print('no statistics')
        return
    print('send statistics median={median}, mean={mean}, count={count}'.format(**stats))
    socketReq.send(encoding.encode(stats))
    data = socketReq.recv()


def getcommand(msg):
    msg = msg[0]
    process(msg)


@timing
def consumer():
    global count
    setInterval(sendStatistics, 2)

    while True:
        if(count == 100000):
            break
        msg = socketPull.recv()
        process(msg)


consumer()
