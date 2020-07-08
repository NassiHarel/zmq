
import zmq
import threading
from util.encoding import Encoding

context = zmq.Context()


def recvStatistics(processStat):

    """Receive Statistics

    receive statistics from all consumers.
    need to sum all proccessed messages by algorithm.
    then decide if need to scale up/down

    """

    print('starting receive statistics...')
    encoding = Encoding("msgpack")
    socketRep = context.socket(zmq.REP)
    socketRep.bind("tcp://*:9023")

    while True:
        msg = socketRep.recv()
        stats = encoding.decode(msg)
        count = stats["count"]
        msgCount = processStat()
        percentage = "{:.2%}".format(count / msgCount)
        print('receive statistics median={median}, mean={mean}, count={count}'.format(**stats))
        print('total handled={count}/{msgCount}, ({percentage})'.format(count=count, msgCount=msgCount, percentage=percentage))
        socketRep.send(b'OK')



def startStatistics(processStat):
    threading.Thread(target=recvStatistics, args=(processStat,)).start()
   
