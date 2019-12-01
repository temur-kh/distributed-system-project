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
    def __init__(self, datanodes, msgs):
        threading.Thread.__init__(self)
        self.datanodes = datanodes
        self.msgs = msgs
    
    def run(self):
        while True:
                        
            for dnode in self.datanodes:
                try:
                    response = requests.post(dnode.getAddress(), json=self.msgs.ping(), timeout=1)
                except(requests.ReadTimeout, requests.ConnectionError):
                    dnode.setStatus(0)
                    continue
                
                dnode.setStatus(1)
                print(f'PING {dnode.getName()}, alive: {response.ok}')

            time.sleep(10)
