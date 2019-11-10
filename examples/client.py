from multiprocessing import Process
import zmq
import json



class Message:
    def __init__(self, socket):
        self.socket = socket

    def send_message(self, message):
        self.socket.send_json(message)

    def recv_message(self):
        return json.loads(self.socket.recv().decode('utf-8'))
    
    def send_init(self):
        message = '''{
            "command": "init",
            "arguments": []
        }'''
        self.send_message(message)

    def recv_init_res(self):
        return self.recv_message()

def function():
    context = zmq.Context()

    print("Connecting to hello world server…")
    socket = context.socket(zmq.DEALER)
    socket.connect("tcp://127.0.0.1:5555")
    msg = Message(socket)
    msg.send_init()
    print(msg.recv_init_res())
    # print(socket.identity)
    # send_message(socket, json.loads('{}'))
    # message = recv_message(socket)
    # print(message)
    # print(socket.recv())

if __name__ == "__main__":
    # msgh = mh.MessageHandler()
    # ft = Process(target=msgh.start())
    # ft.join()
    fn = Process(target=function)
    fn.start()