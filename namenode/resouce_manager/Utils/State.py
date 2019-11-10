import json
import os
import zmq

class Namenode:
    def __init__(self, client_port_number):
        self.cpn = client_port_number

    def getCPN(self):
        return self.cpn


class Datanode:
    def __init__(self, name, ip_address, port_number):
        self.name = name
        self.port = port_number
        self.ip = ip_address
        self.status = False
        self.cid = None
        self.socket = None

    def getName(self):
        return self.name

    def getPort(self):
        return self.port

    def getIp(self):
        return self.ip

    def getStatus(self):
        return self.status

    def setStatus(self, status):
        self.status = status

    def getCid(self):
        return self.cid

    def setCid(self, cid):
        self.cid = cid
    
    def setSocket(self, socket):
        self.socket = socket
        self.socket.connect(f'tcp://{self.ip}:{self.port}')
    
    def getSocket(self):
        return self.socket
    

class Datanodes:
    def __init__(self):
        self.datanodes = []

    def addNewNode(self, name, ip_address, port_number):
        self.datanodes.append(Datanode(name, ip_address, port_number))
    
    def getDatanodes(self):
        return self.datanodes

    def setDatanodeStatuses(self, statuses):
        for i in range(len(self.datanodes)):
            self.datanodes[i].setStatus(statuses[i])

    def getActiveDatanodes(self):
        res = []
        for dnode in self.datanodes:
            if dnode.getStatus():
                res.append(dnode)
        return res


class State:
    def __init__(self, context, configuration_path='configuration.json'):
        self.configuration_path = configuration_path
        self.configuration = self.load_configuration()
        if self.configuration is None:
            raise Exception("Error occurred while initializing node")
        self.parse_configuration()
        self.context = context
        self.initialize_communications()
    
    def load_configuration(self):
        configuration = None
        with open(self.configuration_path) as json_conf:
            # try:
            configuration = json.load(json_conf)
            # except:
            #     print('Error loading configuration')
        
        return configuration

    def parse_configuration(self):
        self.namenode = Namenode(self.configuration['namenode']['client_port_number'])
        self.datanodes = Datanodes()
        dnodes = self.configuration['datanodes']
        for dnode in dnodes:
            self.datanodes.addNewNode(dnode['name'], dnode['ip'], dnode['port'])
    
    def get_datanodes(self):
        return self.datanodes.getDatanodes()
    
    def initialize_communications(self):
        for dnode in self.datanodes.getDatanodes():
            dnode.setSocket(self.context.socket(zmq.DEALER)) #pylint: disable=no-member
    
    def get_available_node(self):
        for dnode in self.get_datanodes():
            if(dnode.getStatus()):
                return dnode
            


# # Checking...
# if __name__ == "__main__":
#     # curD = os.path.curdir
#     # print(os.listdir(curD))
#     state = State()

                

        
        