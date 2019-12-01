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

def send_message(ip, command='init', arguments=[]):
    to_send = json.loads('{}')
    to_send['command'] = command
    to_send['arguments'] = arguments

    try:
        response = requests.post(ip, json=to_send, timeout=2)
    except (requests.ReadTimeout):
        return 1, ''
    except (requests.ConnectionError):
        return 2, ''
    return 0, response

@app.route('/', methods=['GET', 'POST'])
def process():
    print('something')
    omessage = request.get_json(force=True)
    print(omessage)
    if omessage is None:
        return msgs.get_rmessage(verdict=1, message='Wrong command format. Use JSON format')
    
    # command = message['command']
    # arguments = message['arguments']
    print(omessage)
    print(omessage['command'])
    # message_json = json.loads(message)

    code, message = state.tree.perform(omessage)
    print(f'code = {code}, message = {message}')
    if code < 2:
        return msgs.get_rmessage(verdict=code, message=message)
    else:
        nTimes = 5
        while nTimes > 0:
            dnode = state.get_available_node()
            if dnode == None:
                return msgs.get_rmessage(verdict=1, message="No available datanodes")

            else:
                if code == 2:
                    print('Working in 2')
                    # msgj = json.loads(omessage)
                    ver, _ = send_message(dnode.getAddress(), command=omessage['command'], arguments=omessage['arguments'])
                    if ver == 2:
                        dnode.setStatus(0)
                        continue
                    elif ver == 1:
                        nTimes -= 1
                        continue
                    else:
                       return msgs.get_rmessage(verdict=0, message=message) 
                else:
                    print('Working in 3')
                    message = dnode.getAddress()
                    return msgs.get_rmessage(verdict=0, message=message)

        
if __name__ == "__main__":

    msgs = Message()
    state = State()

    pinger = HealthChecker(state.get_datanodes(), msgs)
    pinger.start()

    app.run()
