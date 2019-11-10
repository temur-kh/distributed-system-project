import threading
import zmq
import time
import sys
sys.path.append('/home/abdurasul/Repos/distributed-system-project/utils')
from Message import Message, Messenger #pylint: disable=import-error

class HealthChecker(threading.Thread):
    def __init__(self, context, datanodes, msgs):
        threading.Thread.__init__(self)
        self.datanodes = datanodes
        self.context = context
        self.msgs = msgs
        self.msgh = Messenger(None)
    
    def run(self):
        while True:
            for dnode in self.datanodes:

                self.msgh.setSocket(dnode.getSocket())
                self.msgh.send_message(self.msgs.ping())

                _, message = self.msgh.receive2_message(timeout=1000)
                print(message)
                
                if message == None:
                    dnode.setStatus(0)
                else:
                    wid = message['id']
                    print(f'wid: {wid}, message: {message}')
                    dnode.setStatus(1)
                    dnode.setCid(wid)
                
                print(dnode.getStatus())

            time.sleep(20)


class Handler(threading.Thread):
    def __init__(self, context, wid, state):
        threading.Thread.__init__(self)
        self.context = context
        self.msgh = None
        self.wid = wid
        self.state = state
    
    def run(self):
        self.socket = self.context.socket(zmq.DEALER) #pylint: disable=no-member
        self.socket.connect('inproc://handler')
        self.msgh = Messenger(self.socket)
        self.out_msgh = Messenger(None)
        self.msgs = Message()

        while True:
            cid, message = self.msgh.receive_message()
            print(f'Worker: {self.wid}, Message received: Client id: {cid}, message: {message}')

            print(self.state.get_datanodes())
            node = self.state.get_available_node()
            if node is None:
                message = self.msgs.err_no_datanode()
            else:
                self.out_msgh.setSocket(node.getSocket())
                self.out_msgh.send_message(message)
                wid, response = self.out_msgh.receive2_message(timeout=1000)
                print(f'wid: {wid}, response: {response}')
                message = response
            

            # response = msg.handle(message)
            self.msgh.send2_message(cid, message)