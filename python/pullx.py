import sys
import time
import zmq
import gevent
import statistics
from random import randrange
from zmq.eventloop import ioloop, zmqstream
from util.encoding import Encoding


encoding = Encoding("msgpack")
context = zmq.Context()
socket_pull = context.socket(zmq.PULL)
# socket_pull.setsockopt(zmq.RCVHWM, 1)
# socket_pull.setsockopt(zmq.RCVBUF, 1)
socket_pull.connect("tcp://127.0.0.1:9022")
stream_pull = zmqstream.ZMQStream(socket_pull)
diffs = []
count = 0


def process(msg):
    global count
    count += 1
    # time1 = time.time()
    data = encoding.decode(msg)
    num = data["num"]
    print('receive message {num}'.format(num=num))
    sleep = randrange(10)
    # print('sleeping {sleep} seconds'.format(sleep=sleep))
    # time.sleep(0.01)
    # time2 = time.time()
    # diff = time2 - time1
    diffs.append(sleep)

    if(count % 5 == 0):
        median = statistics.median(diffs)
        mean = statistics.mean(diffs)
        print('median = {median}, mean = {mean}'.format(median=median, mean=mean))
        count = 0
        diffs.clear()


def getcommand(msg):
    msg = msg[0]
    process(msg)


# while True:
#     msg = socket_pull.recv()
#     process(msg)

stream_pull.on_recv(getcommand)
instance = ioloop.IOLoop.instance()
instance.start()
