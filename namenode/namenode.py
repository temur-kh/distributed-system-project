import os
import sys
import json
import requests
from flask import Flask, request, jsonify
from State import State, Datanodes, Datanode
from Handlers import HealthChecker
from Message import Message #pylint: disable=import-error

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../utils'))

app = Flask(__name__)
msgs = None
state = None

@app.route('/', methods=['GET', 'POST'])
def process():
    print('something')
    message = request.get_json(force=True)
    print(message)
    if message is None:
        return msgs.get_rmessage(verdict=1, message='Wrong command format. Use JSON format')
    
    # command = message['command']
    # arguments = message['arguments']
    print(message)
    print(message['command'])
    # message_json = json.loads(message)

    code, message = state.tree.perform(message)
    print(f'code = {code}, message = {message}')
    if code < 2:
        return msgs.get_rmessage(verdict=code, message=message)
        # return json.loads(f'"verdict": {code}, "message": {message}')
    else:
        dnode = state.get_available_node()
        if dnode == None:
            return msgs.get_rmessage(verdict=1, message="No available datanodes")

        else:
            message = dnode.getAddress()
            return msgs.get_rmessage(verdict=0, message=message)
    

        
if __name__ == "__main__":

    msgs = Message()
    state = State()

    pinger = HealthChecker(state.get_datanodes(), msgs)
    pinger.start()

    app.run()
