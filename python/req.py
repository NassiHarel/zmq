import sys
import time
import zmq
import statistics
import threading
from random import randrange
from util.encoding import Encoding
from util.decorators import timing

context = zmq.Context()
encoding = Encoding("msgpack")

socketReq = context.socket(zmq.REQ)
socketReq.connect("tcp://127.0.0.1:9023")
count = 0

import itertools
import logging

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

REQUEST_TIMEOUT = 2500
REQUEST_RETRIES = 3
SERVER_ENDPOINT = "tcp://localhost:5555"

context = zmq.Context()

logging.info("Connecting to server…")
client = context.socket(zmq.REQ)
client.connect(SERVER_ENDPOINT)

for sequence in itertools.count():
    request = str(sequence).encode()
    logging.info("Sending (%s)", request)
    client.send(request)

    retries_left = REQUEST_RETRIES
    while True:
        if (client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
            reply = client.recv()
            logging.info("Resending (%s)", request)
            if False:
                logging.info("Server replied OK (%s)", reply)
                break

        retries_left -= 1
        logging.warning("No response from server")
        # Socket is confused. Close and remove it.
        client.setsockopt(zmq.LINGER, 0)
        client.close()
        if retries_left == 0:
            logging.error("Server seems to be offline, abandoning")
            sys.exit()

        logging.info("Reconnecting to server…")
        # Create new connection
        client = context.socket(zmq.REQ)
        client.connect(SERVER_ENDPOINT)
        logging.info("Resending (%s)", request)
        client.send(request)