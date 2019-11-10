import zmq
from ResourceManager.ResourceManager import ResourceManager #pylint: disable=import-error
from threading import Thread

class Controller:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB) #pylint: disable=no-member
        self.socket.bind('tcp://127.0.0.1:41023')
    
    def interface(self):
        while True:
            command = input()
            if command == 'Terminate':
                self.socket.send(b'1')
                print('terminate command sent')
                exit(0)
            
    def start(self):

        command = Thread(target=self.interface)
        command.start()

        resouceManager = ResourceManager()
        resouceManager.start()
        self.socket.close()
        self.context.term()
        self.context.destroy()
        # resouceManager.join()
        print('resourcemanager finished')
        exit(0)
        return
        
if __name__ == "__main__":
    controller = Controller()
    controller.start()