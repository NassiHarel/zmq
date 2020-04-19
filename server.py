from communication.DataServer import DataServer


def start():
    discovery = {
        'host': '127.0.0.1',
        'port': '9020',
        'encoding': 'msgpack'
    }
    dataServer = DataServer()
    dataServer.listen(discovery['port'])

start()