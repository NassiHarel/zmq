import time
import zmq
from util.encoding import Encoding
from util.decorators import timing


@timing
def producer():
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    # socket.setsockopt(zmq.SNDHWM, 1)
    # socket.setsockopt(zmq.SNDBUF, 1)
    socket.bind("tcp://*:9022")

    encoding = Encoding("msgpack")
    num = 0
    # time1 = time.time()

    while True:
        # time.sleep(0.1)

        if(num == 100000):
            num = 0
            # time2 = time.time()
            # diff = time2 - time1
            # print('took {:.3f} ms'.format((time2 - time1) * 1000.0))
            break

        work_message = encoding.encode({'num': num, "object": {"data": True}, "array": [1, 2, 3, 4, 5]})
        socket.send(work_message, copy=False)
        print('sent message {num}'.format(num=num))
        num += 1


producer()
