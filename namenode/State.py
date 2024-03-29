import json
import os
import copy

class Namenode:
    def __init__(self, client_port_number):
        self.cpn = client_port_number

    def getCPN(self):
        return self.cpn


class Datanode:
    def __init__(self, name, ip_address, port_number, status=-1):
        self.name = name
        self.port = port_number
        self.ip = ip_address
        self.status = status
        self.cid = None

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
    
    def getAddress(self):
        return f'http://{self.ip}:{self.port}'

    def setCid(self, cid):
        self.cid = cid

    def getInfo(self):
        return self.name, self.port, self.ip
    

class Datanodes:
    def __init__(self):
        self.datanodes = []

    def addNewNode(self, name, ip_address, port_number, status=-1):
        for dnode in self.datanodes:
            if dnode.getIp() == ip_address and dnode.getPort() == port_number:
                dnode.setStatus(-1)
                return
        self.datanodes.append(Datanode(name, ip_address, port_number, status))
    
    def getDatanodes(self):
        return self.datanodes

    def setDatanodeStatuses(self, statuses):
        for i in range(len(self.datanodes)):
            self.datanodes[i].setStatus(statuses[i])

    def getActiveDatanodes(self):
        res = []
        for dnode in self.datanodes:
            if dnode.getStatus() == 1:
                res.append(dnode)
        return res
    
    def getDatanodeInfo(self):
        info = []
        for dnode in self.datanodes:
            name, port, ip = dnode.getInfo()
            info.append({"name": name, "ip": ip, "port": port})
        return info



class State:
    def __init__(self, configuration_path='configuration.json'):
        self.configuration_path = configuration_path
        self.configuration = self.load_configuration()
        if self.configuration is None:
            raise Exception("Error occurred while initializing node")
        self.parse_configuration()
        self.tree = Tree()
        self.max_size = 100000
        self.size = 0
    
    def isNew(self):
        return self.size == 0
    
    def load_configuration(self):
        configuration = None
        with open(self.configuration_path) as json_conf:
            # try:
            configuration = json.load(json_conf)
            # except:
            #     print('Error loading configuration')
        
        return configuration
    
    def save_configuration(self):
        conf = {}
        conf['namenode'] = {}
        conf['namenode']['client_port_number'] = self.namenode.getCPN()
        conf['datanodes'] = []
        conf['datanodes'] = self.datanodes.getDatanodeInfo()
        print(conf)
        # conf_json = json.dumps(conf)
        with open(self.configuration_path, 'w') as conf_file:
            json.dump(conf, conf_file)
        
        self.tree.save_configuration()
        
    def parse_configuration(self):
        self.namenode = Namenode(self.configuration['namenode']['client_port_number'])
        self.datanodes = Datanodes()
        dnodes = self.configuration['datanodes']
        for dnode in dnodes:
            self.datanodes.addNewNode(dnode['name'], dnode['ip'], dnode['port'], status=1)
    
    def get_datanodes(self):
        return self.datanodes.getDatanodes()
    
    def get_available_datanodes(self):
        nodes = []
        for dnode in self.get_datanodes():
            if dnode.getStatus() == 1:
                nodes.append(dnode.getAddress())
        return nodes

    def get_available_node(self):
        for dnode in self.get_datanodes():
            if(dnode.getStatus() == 1):
                return dnode
        return None
    
    def setNewSize(self, newSize):
        self.max_size = min(self.max_size, newSize)
    
    def addNewDatanode(self, name=None, ip='127.0.0.1', port=2000):
        if name is None:
            name = 'datanode' + str(len(self.get_datanodes()))
        
        self.datanodes.addNewNode(name=name, ip_address=ip, port_number=port)

class Dir:
    def  __init__(self):
        self.subdir = []
    
    def setValues(self, name, isFile=0, size=0, subdir=[]):
        self.name = name
        self.isFile = isFile
        self.size = size
        for subd in subdir:
            self.subdir.append(subd)

    def __str__(self):
        return f'Name: {self.name}, isFile: {self.isFile}, size: {self.size} subdir len: {len(self.subdir)}'

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name
    
    def getType(self):
        return self.isFile

    def setSize(self, size=0):
        self.size = size
    
    def getSize(self):
        return self.size

    def addSubDir(self, dirs):
        self.subdir.append(copy.copy(dirs))
        pass

    def removeSubDir(self, name):
        # print(f'self: {self.name}, {name}')

        for i in range(len(self.subdir)):
            if self.subdir[i].getName() == name:
                self.subdir.pop(i)
                # print('removed-----------')
                break
    
    def popSubDir(self, name):
        for i in range(len(self.subdir)):
            if self.subdir[i].getName() == name:
                self.subdir.pop(i)
                break
    
    
    def hasSubDir(self, name):
        for d in self.subdir:
            if d.getName() == name:
                return True
        return False
    
    def getSubDir(self, name):
        for d in self.subdir:
            if d.getName() == name:
                return d
        return None

    def getSubDirs(self):
        return self.subdir
    # def addFile(self, File):


class Tree:
    def __init__(self):
        self.root = None

    # def load_conf(self):
    #     conf = None
    #     root = Dir()
    #     root.setName('root')
    #     with open(self.configuration_path) as json_conf:
    #         # try:
    #         conf = json.load(json_conf)
    #     self.conf = conf

    def iterate(self, next_dir):
        print(next_dir)
        for sub in next_dir.subdir:
            self.iterate(sub)

    def is_valid_path(self, path):
        p = path.split('/')
        print(p)
        check_dir = None
        if p[-1] == '':
            check_dir = True
            p.pop()
        curdir = self.root
        history = []
        for c in p[1:]:
            print(c)
            if c == '':
                return False
            if c == '.':
                continue
            if c == '..':
                if len(history) == 0:
                    return False
                curdir = history.pop()
                continue
            if not curdir.hasSubDir(c):
                return False
            history.append(curdir)
            curdir = curdir.getSubDir(c)
        if check_dir:
            return True if curdir.getType() == 0 else False
        return True
    
    def get_current_configuration(self, curdir):
        subdir = []
        print(curdir)
        for sub in curdir.getSubDirs():
            conf_dir = self.get_current_configuration(sub)
            subdir.append(conf_dir)
        conf = {"name": curdir.getName(), "isFile": curdir.getType(), "subdir": subdir}
        return conf
    
    # def save_configuration(self):
    #     conf = self.get_current_configuration(self.root)
    #     with open(self.configuration_path, 'w') as conf_file:
    #         json.dump(conf, conf_file)

    def get_dir(self, path, parent=False):
        p = path.split('/')
        # check_dir = False
        if p[-1] == '':
            # check_dir = True
            p.pop()
        curdir = self.root
        history = []
        last = -1 if parent else 0

        for i in range(1, len(p) + last):
            c = p[i]
            if c == '.':
                continue
            if c == '..':
                if len(history) == 0:
                    return None
                curdir = history.pop()
                continue
            if not curdir.hasSubDir(c):
                return None
            history.append(curdir)
            curdir = curdir.getSubDir(c)
        return curdir
        # if check_dir:
        #     return True if curdir.getType() == 0 else False

    def getDirName(self, path):
        p = path.split('/')
        if p[-1] == '':
            p.pop()
        return p[-1] if p[-1] != '' else None

    def move(self, path1, path2='.'):
        if not self.is_valid_path(path1):
            return 1, 'Invalid source path'
        
        if path2 != '/':
            parent = self.get_dir(path2, parent=True)
            if parent is None:
                return 1, 'Invalid target path'
    
        parentDir = self.get_dir(path1, parent=True)
        directory = self.get_dir(path1)

        if directory.getType() == 0:
            return 1, 'Source is a directory'

        dir_name = self.getDirName(path1)

        if path2 == '/':
            if self.root.hasSubDir(dir_name):
                return 1, 'Target already exists'
            else:
                parentDir.popSubDir(dir_name)
                self.root.addSubDir(directory)
                return 2, 'Successfully moved'

        name = self.getDirName(path2)
        subdir = parent.getSubDir(name)
        if subdir is None:
            parentDir.popSubDir(dir_name)
            directory.setName(name)
            parent.addSubDir(directory)
        else:
            if subdir.getType() == 1:
                return 1, 'Already exists'
            else:
                if subdir.hasSubDir(dir_name):
                    return 1, 'Already exists'
                else:
                    parentDir.popSubDir(dir_name)
                    subdir.addSubDir(directory)
        
        return 2, 'Successfully moved'
    
    def copy_file(self, path1, path2='.'):
        if not self.is_valid_path(path1):
            return 1, 'Invalid source path'
        
        
        if path2 != '/':
            parent = self.get_dir(path2, parent=True)
            if parent is None:
                return 1, 'Invalid target path'

        directory = self.get_dir(path1)
        if directory.getType() == 0:
            return 1, 'Source is a directory'
        
        name = self.getDirName(path2)

        dir_name = directory.getName()

        copy_dir = Dir()
        copy_dir.setValues(directory.getName(), isFile=directory.getType())
        
        if path2 == '/':
            if self.root.hasSubDir(dir_name):
                return 1, 'Target already exists'
            else:
                self.root.addSubDir(copy_dir)
                return 2, 'Successfully copied'

        subdir = parent.getSubDir(name)
        if subdir is None:
            copy_dir.setName(name)
            parent.addSubDir(copy_dir)
        else:
            if subdir.getType() == 1:
                return 1, 'Already exists'
            else:
                if subdir.hasSubDir(dir_name):
                    return 1, 'Already exists'
                else:
                    subdir.addSubDir(copy_dir)
                    
        return 2, 'Successfully copied'
    
    def delete_dir(self, path):
        if not self.is_valid_path(path):
            return 1, 'Invalid path'
        
        parent = self.get_dir(path, parent=True)
        directory = self.getDirName(path)
        parent.removeSubDir(directory)
        return 2, 'Successfully removed'
    
    def delete_file(self, path):
        if not self.is_valid_path(path):
            return 1, 'Invalid path'
        
        file = self.get_dir(path)
        if file.getType() == 0:
            return 1, 'Is a directory'
        parent = self.get_dir(path, parent=True)
        directory = self.getDirName(path)
        parent.removeSubDir(directory)
        return 2, 'Successfully removed'
    
    def make_dir(self, path):
        parent = self.get_dir(path, parent=True)
        if parent is None:
            return 1, 'Invalid path'
        name = self.getDirName(path)
        if parent.hasSubDir(name):
            return 1, 'Already exists'

        new_dir = Dir()
        new_dir.setValues(name=name, isFile=0)
        parent.addSubDir(new_dir)
        return 2, 'Success'
    
    def create_file(self, path):
        parent = self.get_dir(path, parent=True)
        if parent is None:
            return 1, 'Invalid path'

        name = self.getDirName(path)
        if parent.hasSubDir(name):
            return 1, 'Already exists'
        
        new_file = Dir()
        new_file.setValues(name=name, isFile=1)
        parent.addSubDir(new_file)
        return 2, 'Success'

    def info_file(self, path):
        if not self.is_valid_path(path):
            return 1, 'Invalid path'
        file = self.get_dir(path)
        print(f'Path: {path} file name: {file.getName()}, file type: {file.getType()}')
        if file.getType() == 0:
            return 1, 'Is a directory'
        
        info = {}
        info['name'] = file.getName()
        info['size'] = file.getSize()
        message = json.dumps(info)
        return 0, message
    
    def can_write(self, path):
        parent = self.get_dir(path)
        if parent is None:
            return 1, 'Invalid path'
        return 0, 'Success'
    
    def can_read(self, path):
        if not self.is_valid_path(path):
            return 1, 'Invalid path'
        file = self.get_dir(path)
        if file.getType() == 0:
            return 1, 'Is a directory'
        else:
            return 0, 'Success'
    
    def info_dir(self, path):
        if not self.is_valid_path(path):
            return 1, 'Invalid path'
        
        directory = self.get_dir(path)
        if directory.getType() == 1:
            return 1, 'Is a file'
        
        print("-------------------------------------")
        print(directory.getName())
        info = {}
        info['name'] = directory.getName()
        info['subdir'] = []
        for sub in directory.getSubDirs():
            info['subdir'].append({"name": sub.getName(), "isFile": sub.getType()})
        info_string = json.dumps(info)
        return 0, info_string
    
    def write_file(self, path, size=0):
        if path is None:
            return 1, 'Path is not specified'

        parent = self.get_dir(path, parent=True)
        if parent is None:
            return 1, 'Invalid path'

        name = self.getDirName(path)
        if parent.hasSubDir(name):
            return 1, 'Already exists'
        
        new_file = Dir()
        new_file.setValues(name=name, isFile=1, size=size)
        parent.addSubDir(new_file)
        return 3, 'Success'

    def read_file(self, path):
        file = self.get_dir(path)
        if file.getType() != 1:
            return 1, 'Is a directory'
        
        return 3, 'Success'
    
    def init(self):
        self.root = Dir()
        self.root.setValues(name='root')
        return 2, 'Success'
    
    def perform(self, message):
        command = message['command']
        args = message['arguments']
        if command == 'create_file':
            return self.create_file(args[0])
        if command == 'make_dir':
            return self.make_dir(args[0])
        if command == 'delete_file':
            return self.delete_file(args[0])
        if command == 'copy_file':
            return self.copy_file(args[0], args[1])
        if command == 'move_file':
            return self.move(args[0], args[1])
        if command == 'delete_dir':
            return self.delete_dir(args[0])
        if command == 'info_file':
            return self.info_file(args[0])
        if command == 'read_dir':
            return self.info_dir(args[0])
        if command == 'init':
            return self.init()
        if command == 'write_file':
            return self.write_file(path=args[0], size=args[1])
        if command == 'read_file':
            return self.read_file(args[0])
        