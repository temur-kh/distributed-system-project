import json
import requests
import os
import sys

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
        "cpr": "read_file",
        "cpl": "write_file",
        "rm-r": "delete_dir",
        "ls": "read_dir",
        "cd": "read_dir",
        "mkdir": "make_dir",
        "local" : "local"
}


def verify_path(path):
    slash = '/'
    to_verify = path
    for c in list(to_verify):
        if c == slash:
            print(FAIL + "Command denied. Type name of dir without slash signs!")
        else:
            return path
        
def line_split(line):
    line = line + ' '
    t = False
    res = []
    word = ''
    for i in line:
        if (i == '\"'):
            t = not t
            continue
        if (i == ' ' and t) or (i != ' '):
            word = word + i
        elif i == ' ':
            res.append(word)
            word = ''
    return res

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
    return 0
    
def send_message(ip=nip, command='init', arguments=[], file=None):
    to_send = json.loads(json_request)
    to_send['command'] = command
    to_send['arguments'] = arguments

    try:
        if file is not None:
            response = requests.post(ip, json=to_send, files=file)
        else:
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
        if isinstance(p, int):
            args.append(p)
            continue
        if len(p) == 0:
            continue
        if p[0] == '/':
            path = p
        else:
            path = get_abspath(p)
        args.append(os.path.normpath(path))
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

            line = line_split(str(input(get_status_line())))

            if line[0] not in commands:
                if line[0] == 'exit()':
                    pass
                else:
                    print(FAIL + "Command Error. No such command exists!" + ENDC)
            else:
                msg_list = line

                cmd = msg_list[0]

                arguments = msg_list[1:]

                if cmd == 'local':
                    if len(arguments) > 1:
                        print(FAIL + 'Wrong number of arguments' + ENDC)
                        continue
                    
                    path = '.'

                    if len(arguments) != 0:
                        path = arguments[0]
                    
                    if os.path.isdir(path):
                        for file in os.listdir(path):
                            if os.path.isfile(os.path.join(path, file)):
                                print(OKGREEN + file + ENDC)
                            else:
                                print(OKBLUE + file + ENDC)
                    elif os.path.isdir(path):
                        print(FAIL + 'Is a file' + ENDC)
                    else:
                        print(FAIL + 'Invalid path' + ENDC)
                    
                    continue


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
                
                if cmd == 'cpr':
                    if len(arguments) < 1:
                        print(FAIL + 'File is not specified' + ENDC)
                        continue

                    if len(arguments) > 2:
                        print(FAIL + 'Invalid arguments' + ENDC)
                        continue

                    path = get_arguments([arguments[0]])

                    if len(arguments) < 2:
                        savepath = os.path.basename(path[0])
                    elif os.path.isdir(arguments[1]):
                        savepath = os.path.join(arguments[1], os.path.basename(path[0]))
                    else:
                        savepath = arguments[1]
                    # savepath = arguments[1]

                
                if cmd == 'cpl':
                    if len(arguments) < 1:
                        print(FAIL + 'File is not specified' + ENDC)
                        continue
                    if not os.path.isfile(arguments[0]):
                        print(FAIL + 'Invalid path' + ENDC)
                        continue

                    path = '.'
                    if len(arguments) == 2:
                        path = arguments[1]

                    elif len(arguments) > 2:
                        print(FAIL + 'Invalid arguments' + ENDC)
                        continue
                    path = get_arguments([path])[0]
                    savepath = os.path.join(path, os.path.basename(arguments[0]))
                    size = os.path.getsize(arguments[0])
                    sarguments = get_arguments([savepath, size])
                    ver, response = send_message(command=commands[cmd], arguments=sarguments)
                    # filepath = arguments[0]
                    # files = {'file': open(filepath,'rb')}

                else:
                    arguments = get_arguments(arguments)
                    ver, response = send_message(command=commands[cmd], arguments=arguments)

                if ver == 1:
                    continue
                if ver == 2:
                    return
                
                response = response.json()

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

                    elif cmd == 'cpr':
                        datanode = response['message']
                        ver, response = send_message(ip=datanode, command=commands[cmd], arguments=path)
                        if ver != 0:
                            print(FAIL + 'Datanode Connection error' + ENDC)
                            continue
                        response = response.json()
                        file_content = response['message']
                        with open(savepath, 'w') as f:
                            f.write(file_content)

                    elif cmd == 'cpl':
                        filepath = arguments[0]
                        datanode = response['message']

                        with open(filepath, 'r') as f:
                            file_content = f.read()

                        ver, response = send_message(ip=datanode, command=commands[cmd], arguments=[savepath, file_content])
                        if ver != 0:
                            print(FAIL + 'Connection error' + ENDC)
                            continue

                        response = response.json()
                        print(response['message'])
                    
                    elif cmd == 'info':
                        finfo = json.loads(response['message'])
                        print(OKBLUE + f'name: {finfo["name"]}' + ENDC)
                        print(OKBLUE + f'size: {finfo["size"]}' + ENDC)
                        
                    else:
                        print(response['message'])


            if line[0] == 'exit()':
                print(OKGREEN + "Connection has been closed")
                validate['verdict'] = 0
                exit()
    else:
        print(FAIL + "Connection Failed" + ENDC)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Remote server address not specified')
        exit(1)
    nip = f'http://{sys.argv[0]}:{sys.argv[1]}'
    connector()
