import zmq
from multiprocessing import Process
import json
import threading

PING_RESPONSE = '{"id": 1}'
# All incoming messages from namenode consist of fields: "command" and "arguments". See utils/Message.py
# Outgoing messages - not decided yet

def get_ping_response(wid):
    response = json.loads(PING_RESPONSE)
    response['id'] = wid
    return response

class MessageSRHandler:
    def __init__(self, socket, timeout=None):
        self.socket = socket
        if timeout is not None:
            self.RCVTIMEO = timeout
    
    def receive_message(self):
        cid, message_json = self.socket.recv_multipart()
        message = json.loads(message_json)
        return cid, message

    def send_message(self, cid, message):
        self.socket.send_multipart([cid, json.dumps(message).encode('utf-8')])

class Datanode(Process):
    def __init__(self, port):
        Process.__init__(self)
        self.port = port
        
    def run(self):
        
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER) #pylint: disable=no-member
        self.socket.bind(f"tcp://127.0.0.1:{self.port}")
        # self.socket.identity

        self.msgh = MessageSRHandler(self.socket)
        while True:
            cid, message = self.msgh.receive_message()
            print(f'Datanode: {self.port}, cid: {cid}, message = {message}')
            print(self.socket.identity)
            # response = get_ping_response(2)

            self.msgh.send_message(cid, json.loads(PING_RESPONSE))

if __name__ == "__main__":
    datanodes = []
    for i in range(3):
        if i == 1:
            continue
        datanode = Datanode(2000 + i)
        datanode.start()
        datanodes.append(datanode)

    for dn in datanodes:
        dn.join()
    