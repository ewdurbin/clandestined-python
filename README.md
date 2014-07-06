clandestiny
===========

rendezvous hashing implementation based on murmur3 hash


## motiviation

in distributed systems, the need often arises to locate objects amongst a
cluster of machines. consistent hashing and rendezvous hashing are methods of
performing this task, while minimizing data movement on cluster topology
changes.

clandestiny is a library for rendezvous hashing which has the goal of simple
clients and ease of use.

Currently targetting for support:
  - Python 2.5 through Python 3.4

## example usage

```python
from clandestine import Cluster

nodes = {
    '1': {'name': 'node1.example.com', 'zone': 'us-east-1a'},
    '2': {'name': 'node2.example.com', 'zone': 'us-east-1a'},
    '3': {'name': 'node3.example.com', 'zone': 'us-east-1a'},
    '4': {'name': 'node4.example.com', 'zone': 'us-east-1b'},
    '5': {'name': 'node5.example.com', 'zone': 'us-east-1b'},
    '6': {'name': 'node6.example.com', 'zone': 'us-east-1b'},
    '7': {'name': 'node7.example.com', 'zone': 'us-east-1c'},
    '8': {'name': 'node8.example.com', 'zone': 'us-east-1c'},
    '9': {'name': 'node9.example.com', 'zone': 'us-east-1c'},
}

cluster = Cluster(nodes)
nodes = cluster.find_nodes('mykey')
print nodes[0]
print nodes[1]
```

outputs
```
4
8
```

by default, `Cluster` will place 2 replicas around the cluster taking care to
place the second replica in a separate zone from the first.

in the event that your cluster doesn't need zone awareness, you can either
invoke the `RendezvousHash` class directly, or use a `Cluster` with replicas
set to 1

```python
from clandestine import Cluster
from clandestine import RendezvousHash

nodes = {
    '1': {'name': 'node1.example.com'},
    '2': {'name': 'node2.example.com'},
    '3': {'name': 'node3.example.com'},
    '4': {'name': 'node4.example.com'},
    '5': {'name': 'node5.example.com'},
    '6': {'name': 'node6.example.com'},
    '7': {'name': 'node7.example.com'},
    '8': {'name': 'node8.example.com'},
    '9': {'name': 'node9.example.com'},
}

cluster = Cluster(nodes, replicas=1)
rendezvous = RendezvousHash(nodes.keys())

print cluster.find_nodes('mykey')
print rendezvous.find_node('mykey')
```

outputs
```
['4']
4
```
