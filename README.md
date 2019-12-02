## Distributed File Systems

### Description

Academic Project Fall 2019 (Distributive Systems Course)

### Contribution to the project

**Temur Kholmatov** - data node implementation, docker-swarm configuration.

**Abdulkhamid Muminov** - client implementation, system testing.

**Rakhimov Abdurasul** - name node implementation, maintained communication between datanodes, client and name node.

### Requirements 

Install requirements 
`pip install -requirements.txt`


### Running it

* Install requirements

* Create a swarm
  `docker swarm init`

* `docker swarm init-advertise-addr<ip>`

* You will see something like this: 
  ` docker swarm join --token <token_string> <ip>:<port>`

* Run it on your datanode machines to connect to swarm

* Make sure your datanode machines can access the namenode machine and vice verse.

* Run: `docker stack deploy -c docker-compose.yml simple_dfs`

* The namenode container will be located on a leader node

* And other nodes in a swarm (workers) will get one instance of datanode container each

* Use `client.py` from client_side folder to connect to the remote dfs

* Run: `python3 client_side/client.py <ip> <port>`

* Commands allowed: 

  ```
  	"touch" <path>: creates file,
          "rm"	<path>: deletes file,
          "info"	<path>: provides information about the file,
          "cp"	<path>: copies the file,
          "mv"	<path1> <path2>: moves the file,
          "cpr"	<path>: reads the file,
          "cpl"	<path>: writes the file,
          "rm-r"	<path>: deletes the directory,
          "ls"	<path>: reads the directory,
          "cd"	<path>: changes the directory,
          "mkdir"	<path>: creates the directory,
          "local" <path>: provides local files on the client
  ```

  
### Application architecture
![](/res/arch.png)

### Write/Read/Dele flow
![](/res/wrd.png)

### Replication
![](/res/repl.png)


### Github:

https://github.com/temur-kh/distributed-system-project/tree/master

### Dockerhub links:

https://hub.docker.com/repository/docker/temur/datanode
https://hub.docker.com/repository/docker/temur/namenode


### [Here you can overview project architecture](https://docs.google.com/presentation/d/16LXnTU3eRW8o7k3GgPYiyuKM5N5BmlVwBp0HSEidIPE/edit?usp=sharing)
