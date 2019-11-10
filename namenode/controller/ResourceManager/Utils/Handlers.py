import threading
import zmq
import time
import sys
import json
sys.path.append('/home/abdurasul/Repos/distributed-system-project/utils')
from Message import Message, Messenger #pylint: disable=import-error

class HealthChecker(threading.Thread):
    def __init__(self, context, datanodes, msgs):
        threading.Thread.__init__(self)
        self.datanodes = datanodes
        self.context = context
        self.msgs = msgs
        self.msgh = Messenger(None)
        self.socket = self.context.socket(zmq.SUB) #pylint: disable=no-member
        self.socket.connect('tcp://127.0.0.1:41023')
        self.socket.setsockopt(zmq.SUBSCRIBE, b"") #pylint: disable=no-member
        self.socket.RCVTIMEO = 1
        # self.socket.LINGER = 0
    def close(self):
        self.socket.close()
        for dnode in self.datanodes:
            dnode.close()
        self.context.term()
        self.context.destroy()
        exit(1)
    
    def run(self):
        command = None
        while True:
            try:
                command = self.socket.recv()
            except:
                command = None
            
            if command is not None and command == b'1':
                print('Health checker is terminating')
                self.close()
                        
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
                
                print(f'Status = {dnode.getStatus()}')

            time.sleep(10)


class Handler(threading.Thread):
    def __init__(self, context, wid, state):
        threading.Thread.__init__(self)
        self.context = context
        self.msgh = None
        self.wid = wid
        self.state = state
        self.consocket = self.context.socket(zmq.SUB) #pylint: disable=no-member
        self.consocket.connect('tcp://127.0.0.1:41023')
        self.consocket.setsockopt(zmq.SUBSCRIBE, b"") #pylint: disable=no-member
        self.consocket.RCVTIMEO = 1
    
    def close(self):
        self.consocket.close()
        self.socket.close()
        exit(0)
    
    def run(self):
        self.socket = self.context.socket(zmq.DEALER) #pylint: disable=no-member
        self.socket.connect('inproc://handler')
        self.msgh = Messenger(self.socket)
        self.out_msgh = Messenger(None)
        self.msgs = Message()
        # print('handler started')
        while True:
            try:
                command = self.consocket.recv()
            except:
                command = None
            
            if command is not None and command == b'1':
                print(f'Worker {self.wid} is terminating')
                self.close()
            # print(f'worker {self.wid} waiting for incoming message')
            cid, message = self.msgh.receive_message(timeout=1000)
            # print(f'worker {self.wid}, {cid}, {message}')
            if cid == None and message == None:
                continue
            print(f'Worker: {self.wid}, Message received: Client id: {cid}, message: {message}')

            print(self.state.get_datanodes())
            node = self.state.get_available_node()
            if node is None:
                message = self.msgs.err_no_datanode()
                self.msgh.send2_message(cid, message)
                continue
            
            message = json.loads(message)
            command = message['command']
            code, dn_message = self.msgs.get_dmessage(message)
            # dn_message = json.loads(dn_message)
            if code < 0:
                self.msgh.send2_message(cid, dn_message)
                continue
            
            if code == 0:
                verdict, smessage = self.state.tree.perform(message)
                if verdict == 1:
                    message = self.msgs.get_rmessage(verdict=verdict, message=smessage)
                    self.msgh.send2_message(cid, message)
                    continue
                sent_success = False
                while sent_success == False:
                    node = self.state.get_available_node()
                    if node is None:
                        message = self.msgs.err_no_datanode()
                        self.msgh.send2_message(cid, message)
                        continue
                    self.out_msgh.setSocket(node.getSocket())
                    self.out_msgh.send_message(dn_message)
                    wid, response = self.out_msgh.receive2_message(timeout=2000)
                    print(f'received response: {wid}, {response} -------------')
                    if response is not None:
                        sent_success = True

                message = self.msgs.get_rmessage(verdict=verdict, message=smessage)
                self.msgh.send2_message(cid, message)
                continue
        
            if code == 1:
                verdict, smessage = self.state.tree.perform(message)
                message = self.msgs.get_rmessage(verdict=verdict, message=smessage)
                self.msgh.send2_message(cid, message)
                continue

            if code == 2:
                path = message['arguments']
                ver, msg = None, None
                if command == 'read_file':
                    
                    ver, msg = self.state.tree.can_read(path)
                    
                else:
                    ver, msg = self.state.tree.can_write(path)

                if ver == 1:
                    message = self.msgs.get_rmessage(verdict=1, message=msg)
                    self.msgh.send2_message(cid, message)
                else:
                    node = self.state.getStatus()
                    address = f'{node.getIp():{node.getPort()}}'
                    message = self.msgs.get_rmessage(verdict=0, message=msg, other={'address': address})
                    self.msgh.send2_message(cid, message)

                    # if wid == None and response == None:
                    #     pass
                    # else:
                    #     print(f'wid: {wid}, response: {response}')
                    #     if response['verdict'] == 0:

            

            # response = msg.handle(message)
            self.msgh.send2_message(cid, message)

