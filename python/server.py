from communication.ZMQServers import ZMQServers
import gevent
import time


def createBytearray(size):
    return bytearray(b'\xdd'*(size))


result = createBytearray(5)

def start():
    dataServer = ZMQServers(9020, reply)
    job = gevent.spawn(dataServer.listen)
    job.join()


def reply(data):
    time.sleep(10)
    return result
   

start()