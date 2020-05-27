from communication.DataRequest import DataRequest
from util.encoding import Encoding
import gevent


def start():
     request = {
         'port': '9020',
         'host': '127.0.0.1'
     }
     encoding = Encoding("msgpack")

     for i in range(0,500):
          dataRequest = DataRequest(request)
          res = dataRequest.invoke()
     

start()