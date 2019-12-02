import json
import zmq

class Message:
    

    def __init__(self):
        pass

    def get_message(self, command='init', arguments=[]):
        message = json.loads(self.TEMPLATE)
        message['command'] = command
        message['arguments'] = arguments
        return message
    
    def get_rmessage(self, verdict=1, message='', other=()):
        response = json.loads(self.RESPONSE_TEMPLATE)
        response['verdict'] = verdict
        response['message'] = message
        for key, value in other:
            response[key] = value
        return response
    
    
    
    def get_dmessage(self, message):
        print(message['command'])
        # if command == 'init':
        if message['command'] in self.FORWM:
            return 0, message
        
        if message['command'] == 'info_file' or message['command'] == 'read_dir' or message['command'] == 'init':
            return 1, None
        
        if message['command'] == 'write_file' or message['command'] == 'read_file':
            return 2, None

        return -1, self.get_rmessage(verdict=0, message='Invalid command')


    def ping(self):
        return self.get_message(command='PING')

    def cinit(self):
        return self.get_message()

    def ccreate_file(self, path):
        return self.get_message(command='create_file', arguments=[path])
    
    def cdelete_file(self, path):
        return self.get_message(command='delete_file', arguments=[path])
    
    def cinfo_file(self, path):
        return self.get_message(command='info_file', arguments=[path])
    
    def ccopy_file(self, path1, path2='.'):
        return self.get_message(command='copy_file', arguments=[path1, path2])
    
    def cmove_file(self, path1, path2):
        return self.get_message(command='move_file', arguments=[path1, path2])
    
    def cread_file(self, path):
        return self.get_message(command='read_file', arguments=[path])
    
    def cwrite_file(self, path, size=0):
        return self.get_message(command='write_file', arguments=[path, size])
    
    def cdelete_dir(self, path):
        return self.get_message(command='delete_dir', arguments=[path])
    
    def cread_dir(self, path):
        return self.get_message(command='read_dir', arguments=[path])
    
    def cmake_dir(self, path):
        return self.get_message(command='make_dir', arguments=[path])
    
    def err_no_datanode(self):
        return json.loads(self.ERROR_NO_AVAILABLE_NODE)

    ERROR_NO_AVAILABLE_NODE = '{"verdict": 0, "message": "No available datanode. Try connecting later"}'
    TEMPLATE = '{"command": "", "arguments": []}'
    RESPONSE_TEMPLATE = '{"verdict": 1, "message": ""}'
    PING = '{"command": "PING", "arguments": []}'
    CLIENT_INIT = '{"command": "init", "arguments": []}'
    CLIENT_CREATE_FILE = '{"command": "create_file", "arguments": []}'
    CLIENT_DELETE_FILE = '{"command": "delete_file", "arguments": []}'
    CLIENT_INFO_FILE = '{"command": "info_file", "arguments": []}'
    CLIENT_COPY_FILE = '{"command": "copy_file", "arguments": []}'
    CLIENT_MOVE_FILE = '{"command": "move_file", "arguments": []}'
    
    CLIENT_READ_FILE = '{"command": "read_file", "arguments": []}'
    CLIENT_WRITE_FILE = '{"command": "write_file", "arguemnts": []}'

    CLIENT_DELETE_DIR = '{"command": "delete_dir", "arguments": []}'
    CLIENT_READ_DIR = '{"command": "read_dir", "arguments": []}'
    CLIENT_MAKE_DIR = '{"command": "make_dir", "arguments": []}'

    FORWM = [
        'create_file',
        'delete_file',
        'copy_file',
        'move_file',
        'delete_dir',
        'make_dir'
    ]



    # CLIENT_RESPONSE_OK = json.loads('{"verdict": 1, "message": ""}')
    # CLIENT_RESPONSE_FAIL = json.loads


class Messenger:
    def __init__(self, socket):
        self.socket = socket
        # self.timeout = timeout
        # if timeout is not None:
        #     self.socket.RCVTIMEO = self.timeout

    def send_message(self, message):
        self.socket.send_json(message)
    
    def send2_message(self, cid, message):
        self.socket.send_multipart([cid, json.dumps(message).encode('utf-8')])

    def receive_message(self, timeout=None):
        if timeout is not None:
            self.socket.RCVTIMEO = timeout
        cid, received = None, None
        try:
            cid, received = self.socket.recv_multipart()
        except:
            return None, None
        # self.socket.RCVTIMEO = self.timeout
        return cid, json.loads(received.decode('utf-8'))
    
    def receive2_message(self, timeout=None):
        if timeout is not None:
            self.socket.RCVTIMEO = timeout
        cid, received = None, None
        try:
            received = self.socket.recv_json()
        except:
            return None, None
        
        # self.socket.RCVTIMEO = self.timeout
        return cid, received
    
    def setSocket(self, socket):
        self.socket = socket