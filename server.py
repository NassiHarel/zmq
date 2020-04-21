from communication.DataServer import DataServer
import gevent


mb = 1024 * 1024

def create_bytearray(sizeBytes):
    return bytearray(b'\xdd'*(sizeBytes * mb))
    
data = create_bytearray(5000)

def start():
    port = '9020'
    dataServer = DataServer(reply)
    job = gevent.spawn(dataServer.listen,port)
    job.join()


def reply():
    return data


start()