from multiprocessing import Process
import zmq
import json

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

global_path = '~/'

curr_path = ['~']

status_line = OKGREEN + "namenode:" + ENDC + ":" + OKBLUE + '/'.join(curr_path) + ENDC + " $ "

# Making request JSON for the namenode
json_request = '''{
                    "command": "",
                    "arguments": []
                }
                '''
commands = {
    "commands": {
        "touch": "create_file",
        "rm": "delete_file",
        "info": "info_file",
        "cp": "copy_file",
        "mv": "move_file",
        "r--": "read_file",
        "rw-": "write_file",
        "rm-r": "delete_dir",
        "ls": "read_dir",
        "cd": "read_dir",
        "mkdir": "make_dir"
    }
}


class Message:
    def __init__(self, socket):
        self.socket = socket

    def send_message(self, message):
        self.socket.send_json(message)

    def recv_message(self):
        return json.loads(self.socket.recv().decode('utf-8'))

    def send_init(self):
        message = '''{
            "command": "info_file",
            "arguments": [" "]
        }'''
        self.send_message(message)

    def recv_init_res(self):
        return self.recv_message()


def verify_path(path):
    slash = '/'
    to_verify = path
    for c in list(to_verify):
        if c == slash:
            print(FAIL + "Command denied. Type name of dir without slash signs!")
        else:
            return path


def cdirectory(path, curr_path=curr_path):
    curr_path = curr_path + path
    return curr_path


# TODO Implement 'cd' command
def print_path(path):
    string = ''
    for i in range(0, len(path)):
        string += path[i] + '/'
    return string


def cd(curr, target):
    global curr_path
    if target in curr_path:
        pass


def connector():
    global curr_path
    global status_line
    print("Type in IP address: ")
    ip = "tcp://127.0.0.1:5555"

    context = zmq.Context()
    # Initialising sockets to initiate connection
    print("Connecting to the name-node..")

    socket = context.socket(zmq.DEALER)
    socket.connect(ip)

    init_connection = Message(socket)
    init_connection.send_init()

    # Validating connection based on verdict of the namenode
    validate = init_connection.recv_init_res()
    print(validate)

    if validate['verdict'] == 1:
        print(OKBLUE + "Connection established. Type in commands" + ENDC)

        # Getting commands while connection is active
        while validate['verdict'] == 1:

            line = str(input(status_line)).split(' ')

            if line[0] not in commands['commands']:
                if line[0] == 'exit()':
                    pass
                else:
                    print(FAIL + "Command Error. No such command exists!" + ENDC)
            else:
                msg_list = line

                cmd = msg_list[0]

                arguments = msg_list[1:]

                # TODO Switch cases for commands
                # if cmd == 'cd':
                #     curr_path.append(arguments[0])
                #     print('/'.join(curr_path))

                to_send = json.loads(json_request)
                to_send['command'] = commands['commands'][cmd]
                to_send['arguments'] = arguments
                to_send = json.dumps(to_send)

                print(to_send)

                request = Message(socket)
                request.send_message(to_send)

                response = request.recv_message()
                print(response['verdict'])
                print(response)

                if response['verdict'] == 1:
                    print(FAIL + response['message'] + ENDC)

                else:
                    if cmd == 'ls':
                        print(response['message'])
                    if cmd == 'touch':
                        print("File has been created")
                    if cmd == 'rm':
                        print("File has been deleted")
                    if cmd == 'info':
                        print(response['message'])
                    if cmd == 'cp':
                        print(response['message'])
                    if cmd == 'mv':
                        print(response['message'])
                    if cmd == 'r--':
                        print(response['message'])
                    if cmd == 'rw-':
                        print(response['message'])
                    if cmd == 'rm-r':
                        print(response['message'])
                    if cmd == 'mkdir':
                        print(response['message'])

                    print('>> ' + response['message'])

            if line[0] == 'exit()':
                print(OKGREEN + "Connection had been closed")
                validate['verdict'] = 0
                exit()
    else:
        print(FAIL + "Connection Failed" + ENDC)


if __name__ == '__main__':
    connector()
    # fn = Process(target=connector)
    # fn.start()
