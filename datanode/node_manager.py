from flask import Flask
from flask import request
from threading import Thread
import json
import sys
from pprint import pprint
from datanode.handlers import *
import os
import requests


PING_RESPONSE = {"id": 1}
DATANODE_ADDRESSES = set()
NAMENODE = ''

app = Flask(__name__)


class DataNodePropagate(Thread):
    def __init__(self, url, data):
        Thread.__init__(self)
        self.url = url
        self.data = data

    def run(self):
        tries = 0
        while tries < 3:
            resp = requests.get(self.url, json=self.data)
            if resp.json()['verdict'] == 0:
                break
            tries += 1


def request_datanodes_info():
    res = requests.get(NAMENODE, json={'command': 'dn_list'})
    add_nodes(res.json())


def propagate(request):
    for node in DATANODE_ADDRESSES:
        print(node)
        url = os.path.join(node, '/')
        print(url)
        data = request.get_json()
        data['arguments'] = []
        conn = DataNodePropagate(url, data)
        conn.start()


def add_nodes(json_data):
    if 'arguments' not in json_data:
        for addr in json_data['arguments']:
            DATANODE_ADDRESSES.add(addr)
        return {'verdict': 0, 'message': 'New datanodes were memorized.'}
    else:
        return {'verdict': 1, 'message': 'No arguments are provided.'}


def remove_nodes(json_data):
    if 'arguments' not in json_data:
        for addr in json_data['arguments']:
            DATANODE_ADDRESSES.remove(addr)
        return {'verdict': 0, 'message': 'Old datanodes were forgotten.'}
    else:
        return {'verdict': 1, 'message': 'No arguments are provided.'}


@app.route('/', methods=['POST'])
def post_request():
    json_data = request.get_json()
    pprint(json_data)
    try:
        cmd = json_data['command']
    except KeyError:
        return json.dumps({'verdict': 1, 'message': 'The request does not contain command field.'})

    if cmd == 'write_file':
        result = write_file(app, request)
        propagate(request)
    else:
        result = {'verdict': 1, 'message': 'The command is invalid.'}

    return json.dumps(result)

@app.route('/', methods=['GET'])
def get_request():
    json_data = request.get_json()
    try:
        cmd = json_data['command']
    except KeyError:
        return json.dumps({'verdict': 1, 'message': 'The request does not contain command field.'})

    if cmd == 'init':
        result = init(app, request)
        propagate(request)
    elif cmd == 'create_file':
        result = create_file(app, request)
        propagate(request)
    elif cmd == 'delete_file':
        result = delete_file_or_dir(app, request)
        propagate(request)
    elif cmd == 'copy_file':
        result = copy_file(app, request)
        propagate(request)
    elif cmd == 'move_file':
        result = move_file(app, request)
        propagate(request)
    elif cmd == 'read_file':
        result = read_file(app, request)
    elif cmd == 'delete_dir':
        result = delete_file_or_dir(app, request)
        propagate(request)
    elif cmd == 'read_dir':
        result = read_dir(app, request)
    elif cmd == 'make_dir':
        result = make_dir(app, request)
        propagate(request)
    elif cmd == 'PING':
        result = PING_RESPONSE
    elif cmd == 'NEW_NODE':
        result = add_nodes(request.get_json())
    elif cmd == "DELETE_NODE":
        result = remove_nodes(request.get_json())
    elif cmd == "repl":
        result = replicate(app, request)
    else:
        result = {'verdict': 1, 'message': 'The command is invalid.'}
        pass

    return result


if __name__ == "__main__":
    if len(sys.argv) == 3:
        NAMENODE = sys.argv[1]
        root = sys.argv[2]
    else:
        raise ValueError('The arguments provided are incorrect.')
    app.config['root'] = root
    # request_datanodes_info()
    app.run(debug=True, host='0.0.0.0')
