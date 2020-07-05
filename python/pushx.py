import time
import zmq
from util.encoding import Encoding
from util.decorators import timing


@timing
def producer():
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.setsockopt(zmq.SNDHWM, 1)
    socket.setsockopt(zmq.SNDBUF, 1)
    socket.bind("tcp://*:9022")

    encoding = Encoding("msgpack")
    num = 0

    while True:
        # time.sleep(0.001)
        num += 1
        # if(num == 20):
        #     break

        work_message = encoding.encode({'num': num, "object": {"data": True}, "array": [1, 2, 3, 4, 5]})
        socket.send(work_message, copy=False)
        print('sent message {num}'.format(num=num))


producer()
