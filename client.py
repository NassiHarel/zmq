from communication.DataRequest import DataRequest
from util.decorators import timing
from util.encoding import Encoding

def start():
     request = {
         'port': '9020',
         'host': '127.0.0.1'
     }
     dataRequest = DataRequest(request)
     res = dataRequest.invoke()
     view = memoryview(res.bytes)
     totalLength = len(view)
     ver = bytes(view[0:1])
     print(ver)


start()