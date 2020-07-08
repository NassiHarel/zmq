import sys
import time
import zmq
import statistics
import threading
from random import randrange
from util.encoding import Encoding

context = zmq.Context()
encoding = Encoding("msgpack")

diffs = []
count = 0
stats = None

def processStat():
    global count
    global stats
    count += 1
   
    random = randrange(10)
    diffs.append(random)

    if(count % 5 == 0):
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


