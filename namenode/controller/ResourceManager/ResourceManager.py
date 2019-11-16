import zmq
import json
import threading
from .Utils.State import State #pylint: disable=import-error
from .Utils.Handlers import HealthChecker, Handler #pylint: disable=import-error
import time
import sys
import os
# sys.path.append(os.path.join(os.path.curdir, './distributed-system-project/utils'))
from utils.Message import Message #pylint: disable=import-error
import multiprocessing

class ResourceManager(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.socket_client = None
        self.context = None
        self.state = None
        self.msgs = Message()

    def start(self):
        print('ResourceManager started')
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
        print('everything is started')

        try:
            zmq.proxy(self.socket_client, self.handler) #pylint: disable=no-member
        except zmq.ContextTerminated:
            print('context terminated')


        # for w in workers:
        #     w.join()
        # pinger.join()

        print('stopp---------------------------------------------------------------------------------------ed')

        self.state.save_configuration()


# if __name__ == "__main__":
#     msgh = ResourceManager()
#     msgh.start()
