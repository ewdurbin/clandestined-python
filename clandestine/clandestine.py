
from collections import defaultdict

from ._murmur3 import murmur3_32


class RendezvousHash(object):

    def __init__(self, nodes=None, murmur_seed=0, hash_function=murmur3_32):
        self.nodes = []
        self.murmur_seed = murmur_seed
        if nodes is not None:
            self.nodes = nodes
        if hash_function == murmur3_32:
            self.hash_function = lambda x: hash_function(x, murmur_seed)
        elif murmur_seed != 0:
            raise ValueError("Do not know how to set murmur_seed on %s" %
                             (hash_function.__name__))
        else:
            self.hash_function = hash_function

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)

    def remove_node(self, node):
        if node in self.nodes:
            self.nodes.remove(node)

    def find_node(self, key):
        return max(self.nodes, key=lambda x:
                   self.hash_function("%s-%s" % (str(x), str(key))))


class Cluster(object):

    def __init__(self, cluster_config=None, replicas=2,
                 murmur_seed=0, hash_function=murmur3_32):
        self.murmur_seed = murmur_seed
        if hash_function == murmur3_32:
            self.hash_function = lambda x: hash_function(x, murmur_seed)
        elif murmur_seed != 0:
            raise ValueError("Do not know how to set murmur_seed on %s" %
                             (hash_function.__name__))
        else:
            self.hash_function = hash_function

        def RendezvousHashConstructor():
            return RendezvousHash(nodes=None, hash_function=self.hash_function)

        self.replicas = replicas
        self.nodes = {}
        self.zones = []
        self.zone_members = defaultdict(list)
        self.rings = defaultdict(RendezvousHashConstructor)

        if cluster_config is not None:
            for node, node_data in cluster_config.items():
                name = node_data.get('name', None)
                zone = node_data.get('zone', None)
                self.add_node(node, node_name=name, node_zone=zone)

    def add_zone(self, zone):
        if zone not in self.zones:
            self.zones.append(zone)
            self.zones = sorted(self.zones)

    def remove_zone(self, zone):
        if zone in self.zones:
            self.zones.remove(zone)
            for member in self.zone_members[zone]:
                self.nodes.remove(member)
            self.zones = sorted(self.zones)
            del self.rings[zone]
            del self.zone_members[zone]

    def add_node(self, node_id, node_zone=None, node_name=None):
        if node_id in self.nodes.keys():
            raise ValueError('Node with name %s already exists', node_id)
        self.add_zone(node_zone)
        self.rings[node_zone].add_node(node_id)
        self.nodes[node_id] = node_name
        self.zone_members[node_zone].append(node_id)

    def remove_node(self, node_id, node_name=None, node_zone=None):
        self.rings[node_zone].remove_node(node_id)
        del self.nodes[node_id]
        self.zone_members[node_zone].remove(node_id)
        if len(self.zone_members[node_zone]) == 0:
            self.remove_zone(node_zone)

    def node_name(self, node_id):
        return self.nodes.get(node_id, None)

    def find_nodes(self, key, offset=None):
        nodes = []
        if offset is None:
            offset = sum([ord(char) for char in key]) % len(self.zones)
        for i in range(self.replicas):
            zone = self.zones[(i + offset) % len(self.zones)]
            ring = self.rings[zone]
            nodes.append(ring.find_node(key))
        return nodes

    def find_nodes_by_index(self, partition_id, key_index):
        offset = int(partition_id) + int(key_index) % len(self.zones)
        key = "%s-%s" % (partition_id, key_index)
        return self.find_nodes(key, offset=offset)
