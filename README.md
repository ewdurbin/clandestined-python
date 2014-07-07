clandestined
===========

rendezvous hashing implementation based on murmur3 hash


## motiviation

in distributed systems, the need often arises to locate objects amongst a
cluster of machines. consistent hashing and rendezvous hashing are methods of
performing this task, while minimizing data movement on cluster topology
changes.

clandestined is a library for rendezvous hashing which has the goal of simple
clients and ease of use.

Currently targetting for support:
  - Python 2.5 through Python 3.4

[![Build Status](https://travis-ci.org/ewdurbin/clandestined-python.svg?branch=master)](https://travis-ci.org/ewdurbin/clandestined-python)

## example usage

```python
>>> from clandestined import Cluster
>>>
>>> nodes = {
...     '1': {'name': 'node1.example.com', 'zone': 'us-east-1a'},
...     '2': {'name': 'node2.example.com', 'zone': 'us-east-1a'},
...     '3': {'name': 'node3.example.com', 'zone': 'us-east-1a'},
...     '4': {'name': 'node4.example.com', 'zone': 'us-east-1b'},
...     '5': {'name': 'node5.example.com', 'zone': 'us-east-1b'},
...     '6': {'name': 'node6.example.com', 'zone': 'us-east-1b'},
...     '7': {'name': 'node7.example.com', 'zone': 'us-east-1c'},
...     '8': {'name': 'node8.example.com', 'zone': 'us-east-1c'},
...     '9': {'name': 'node9.example.com', 'zone': 'us-east-1c'},
... }
>>>
>>> cluster = Cluster(nodes)
>>> cluster.find_nodes('mykey')
['4', '8']
>>>
```

by default, `Cluster` will place 2 replicas around the cluster taking care to
place the second replica in a separate zone from the first.

in the event that your cluster doesn't need zone awareness, you can either
invoke the `RendezvousHash` class directly, or use a `Cluster` with replicas
set to 1

```python
>>> from clandestined import Cluster
>>> from clandestined import RendezvousHash
>>>
>>> nodes = {
...     '1': {'name': 'node1.example.com'},
...     '2': {'name': 'node2.example.com'},
...     '3': {'name': 'node3.example.com'},
...     '4': {'name': 'node4.example.com'},
...     '5': {'name': 'node5.example.com'},
...     '6': {'name': 'node6.example.com'},
...     '7': {'name': 'node7.example.com'},
...     '8': {'name': 'node8.example.com'},
...     '9': {'name': 'node9.example.com'},
... }
>>>
>>> cluster = Cluster(nodes, replicas=1)
>>> rendezvous = RendezvousHash(nodes.keys())
>>>
>>> cluster.find_nodes('mykey')
['4']
>>> rendezvous.find_node('mykey')
'4'
>>>
```

## advanced usage

### murmur3 seeding

if you plan to use keys based on untrusted input (not really supported, but go
ahead), it would be best to use a custom seed for hashing. although this
technique is by no means a way to fully mitigate a DoS attack using crafted
keys, it may make you sleep better at night.

```python
>>> from clandestined import Cluster
>>> from clandestined import RendezvousHash
>>>
>>> nodes = {
...     '1': {'name': 'node1.example.com'},
...     '2': {'name': 'node2.example.com'},
...     '3': {'name': 'node3.example.com'},
...     '4': {'name': 'node4.example.com'},
...     '5': {'name': 'node5.example.com'},
...     '6': {'name': 'node6.example.com'},
...     '7': {'name': 'node7.example.com'},
...     '8': {'name': 'node8.example.com'},
...     '9': {'name': 'node9.example.com'},
... }
>>>
>>> cluster = Cluster(nodes, replicas=1, murmur_seed=1337)
>>> rendezvous = RendezvousHash(nodes.keys(), murmur_seed=1337)
>>>
>>> cluster.find_nodes('mykey')
['7']
>>> rendezvous.find_node('mykey')
'7'
>>>
```

### supplying your own hash function

a more robust, but possibly slower solution to mitigate DoS vulnerability by
crafted key might be to supply your own cryptograpic hash function.

in order for this to work, your method must be supplied to the `RendezvousHash`
or `Cluster` object as a callable which takes a byte string `key` and returns
an integer.

```python
>>> import hashlib
>>> from clandestined import Cluster
>>> from clandestined import RendezvousHash
>>>
>>> nodes = {
...     '1': {'name': 'node1.example.com'},
...     '2': {'name': 'node2.example.com'},
...     '3': {'name': 'node3.example.com'},
...     '4': {'name': 'node4.example.com'},
...     '5': {'name': 'node5.example.com'},
...     '6': {'name': 'node6.example.com'},
...     '7': {'name': 'node7.example.com'},
...     '8': {'name': 'node8.example.com'},
...     '9': {'name': 'node9.example.com'},
... }
>>>
>>> def my_hash_function(key):
...     return int(hashlib.sha1(key.encode('utf-8')).hexdigest(), 16)
...
>>>
>>> cluster = Cluster(nodes, replicas=1, hash_function=my_hash_function)
>>> rendezvous = RendezvousHash(nodes.keys(), hash_function=my_hash_function)
>>>
>>> cluster.find_nodes('mykey')
['1']
>>> rendezvous.find_node('mykey')
'1'
>>>
```
