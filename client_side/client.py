from multiprocessing import Process
import zmq
import json
import requests
import os

nip = "http://127.0.0.1:5000"

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

global_path = '~/'
root = '/'
curr_path = '/'

def get_status_line():
    status_line = OKGREEN + "namenode:" + ENDC + ":" + OKBLUE + curr_path + ENDC + " $ "
    return status_line

# Making request JSON for the namenode
json_request = '''{
                    "command": "",
                    "arguments": []
                }
                '''
commands = {
    
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

def change_directory(path=''):
    global curr_path
    if len(path) < 1:
        curr_path = root
        return 0
    
    if path[0] != '/':
        path = os.path.join(curr_path, path)
    
    ver, response = send_message(command='read_dir', arguments=[path])
    if ver != 0:
        print(FAIL + response + ENDC)
        return 1

    response = response.json()
    if response['verdict'] == 1:
        print(FAIL + response['message'] + ENDC)
        return 1
    
    curr_path = os.path.normpath(path)
    # print(f'current path = {curr_path}')
    return 0
    
def send_message(ip=nip, command='init', arguments=[]):
    to_send = json.loads(json_request)
    to_send['command'] = command
    to_send['arguments'] = arguments
    # print(f'Sending: {to_send}')

    try:
        response = requests.post(ip, json=to_send)
    except (requests.ReadTimeout):
        print(FAIL + "Connection timed out" + ENDC)
        return 1, ''
    except (requests.ConnectionError):
        print(FAIL + "Remote namenode connection failed" + ENDC)
        return 2, ''
    return 0, response

def get_abspath(path):
    return os.path.join(curr_path, path)

def get_arguments(arguments):
    args = []
    for p in arguments:
        if len(p) == 0:
            continue
        if p[0] == '/':
            args.append(p)
        else:
            args.append(get_abspath(p))
    return args    

def connector():
    global curr_path
    # print("Type in IP address: ")
    

    # Initialising sockets to initiate connection
    print("Connecting to the name-node..")

    #Initializing...
    ver, response = send_message()
    if ver != 0:
        print(FAIL + "Connection Failed" + ENDC)
        return

    validate = response.json()
    if validate['verdict'] == 0:
        print(OKBLUE + "Connection established. Type in commands" + ENDC)

        # Getting commands while connection is active
        while validate['verdict'] == 0:

            line = str(input(get_status_line())).split(' ')

            if line[0] not in commands:
                if line[0] == 'exit()':
                    pass
                else:
                    print(FAIL + "Command Error. No such command exists!" + ENDC)
            else:
                msg_list = line

                cmd = msg_list[0]

                arguments = msg_list[1:]

                if cmd == 'cd':
                    if len(arguments) > 0:
                        path = arguments[0]
                    else:
                        path = ''
                    ret = change_directory(path)
                    if ret == 2:
                        return
                    continue

                if cmd == 'ls':
                    if len(arguments) == 0 :
                        arguments = [curr_path]

                arguments = get_arguments(arguments)
                ver, response = send_message(command=commands[cmd], arguments=arguments)

                if ver == 1:
                    continue
                if ver == 2:
                    return
                
                response = response.json()
                # print(response['verdict'])
                # print(response)

                if response['verdict'] == 1:
                    print(FAIL + response['message'] + ENDC)

                else:
                    if cmd == 'ls':
                        directory = json.loads(response['message'])
                        for dirs in directory['subdir']:
                            if dirs['isFile']:
                                print(OKGREEN + dirs['name'] + ENDC)
                            else:
                                print(OKBLUE + dirs['name'] + ENDC)

                    elif cmd == 'touch':
                        print("File has been created")
                    elif cmd == 'rm':
                        print("File has been deleted")
                    else:
                        #  cmd == 'info':
                        print(response['message'])
                    # if cmd == 'cp':
                    #     print(response['message'])
                    # if cmd == 'mv':
                    #     print(response['message'])
                    # if cmd == 'r--':
                    #     print(response['message'])
                    # if cmd == 'rw-':
                    #     print(response['message'])
                    # if cmd == 'rm-r':
                    #     print(response['message'])
                    # if cmd == 'mkdir':
                    #     print(response['message'])

                    # print('>> ' + response['message'])

            if line[0] == 'exit()':
                print(OKGREEN + "Connection has been closed")
                validate['verdict'] = 0
                exit()
    else:
        print(FAIL + "Connection Failed" + ENDC)


if __name__ == '__main__':
    connector()
    # fn = Process(target=connector)
    # fn.start()
