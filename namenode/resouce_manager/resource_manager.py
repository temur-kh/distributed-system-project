import zmq
import json
import threading
from Utils.State import State
from Utils.Handlers import HealthChecker, Handler
import time
import sys
sys.path.append('/home/abdurasul/Repos/distributed-system-project/utils')
from Message import Message #pylint: disable=import-error

class ResourceManager:
    def __init__(self):
        self.socket_client = None
        self.context = None
        self.state = None
        self.msgs = Message()

    def start(self):
        self.context = zmq.Context()
        self.socket_client = self.context.socket(zmq.ROUTER) #pylint: disable=no-member
        self.socket_client.bind("tcp://127.0.0.1:5555")

        self.state = State(self.context)

        # self.socket_datanode = self.context.socket(zmq.ROUTER)
        # self.socket_datanode.bind("tcp:/127.0.0.1:32153")

        self.handler = self.context.socket(zmq.DEALER) #pylint: disable=no-member
        self.handler.bind('inproc://handler')

        workers = []
        for wid in range(5):
            worker = Handler(self.context, wid, self.state)
            worker.start()
            workers.append(worker)

        pinger = HealthChecker(self.context, self.state.get_datanodes(), self.msgs)
        pinger.start()

        zmq.proxy(self.socket_client, self.handler) #pylint: disable=no-member


        for w in workers:
            w.join()
        pinger.join()


if __name__ == "__main__":
    msgh = ResourceManager()
    msgh.start()
