import threading
import os
import zmq
import time
import sys
import json
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../utils'))
from Message import Message, Messenger #pylint: disable=import-error
import requests
from flask import Flask, request, jsonify


class HealthChecker(threading.Thread):
    def __init__(self, state, msgs):
        threading.Thread.__init__(self)
        self.state = state
        self.msgs = msgs
    
    def run(self):
        while True:
            repl_node = None
            delete_nodes = []
            for dnode in self.state.get_datanodes():
                if dnode.getStatus() < 1:
                    continue
                try:
                    response = requests.post(dnode.getAddress(), json=self.msgs.ping(), timeout=1)
                except(requests.ReadTimeout, requests.ConnectionError):
                    if dnode.getStatus() == 1:
                        delete_nodes.append(dnode.getAddress())
                    dnode.setStatus(0)
                    continue
                repl_node = dnode
                print(f'PING {dnode.getName()}, alive: {response.ok}')
            
            # Updating datanode information in datanodes
            if len(delete_nodes) > 0:
                for dnode in self.state.get_datanodes():
                    try:
                        response = requests.post(dnode.getAddress(), json=self.msgs.get_message(command='DELETE_NODE', arguments=delete_nodes), timeout=1)
                    except(requests.ReadTimeout, requests.ConnectionError):
                        continue
            
            if repl_node is None:
                continue
        
            new_nodes = []

            for dnode in self.state.get_datanodes():
                if dnode.getStatus() == -1:
                    
                    try:
                        response = requests.post(dnode.getAddress(), json=self.msgs.get_message(command='repl', arguments=[repl_node.getAddress()]), timeout=1)
                    except(requests.ReadTimeout, requests.ConnectionError):
                        continue
                    
                    new_nodes.append(dnode.getAddress())
                    dnode.setStatus(1)
            
            # Updating datanode information in datanodes
            if len(new_nodes) > 0:
                for dnode in self.state.get_datanodes():
                    try:
                        response = requests.post(dnode.getAddress(), json=self.msgs.get_message(command='NEW_NODE', arguments=new_nodes), timeout=1)
                    except(requests.ReadTimeout, requests.ConnectionError):
                        continue


            time.sleep(3)
