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


def process(msg):
    time1 = time.time()
    data = encoding.decode(msg)
    num = data["num"]
    print('receive message {num}'.format(num=num))
    sleep = randrange(5)
    print('sleeping {sleep} seconds'.format(sleep=sleep))
    time.sleep(sleep)
    time2 = time.time()
    diff = time2 - time1
    diffs.append(diff)

    if(num == 20):
        statistics.median(list_name)


def getcommand(msg):
    msg = msg[0]
    process(msg)


# while True:
#     msg = socket_pull.recv()
#     process(msg)

stream_pull.on_recv(getcommand)
instance = ioloop.IOLoop.instance()
instance.start()
