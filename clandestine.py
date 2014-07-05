
from collections import defaultdict

from murmur3 import murmur3_x86_32


class RendezvousHash(object):

    def __init__(self, nodes=None, hash_function=murmur3_x86_32):
        self.nodes = []
        if nodes is not None:
            self.nodes = nodes
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

    def __init__(self, cluster, hash_function=murmur3_x86_32, replicas=2):
        self.hash_function = hash_function

        def RendezvousHashConstructor():
            return RendezvousHash(nodes=None, hash_function=self.hash_function)

        self.replicas = replicas
        self.nodes = {}
        self.zones = []
        self.zone_members = defaultdict(list)
        self.rings = defaultdict(RendezvousHashConstructor)

        for node, node_data in cluster.items():
            name = node_data.get('name', None)
            zone = node_data.get('zone', None)
            self.add_zone(zone)
            self.add_node(node, node_name=name, node_zone=zone)

    def add_zone(self, zone):
        if zone not in self.zones:
            self.zones.append(zone)
            self.zones = sorted(self.zones)

    def remove_zone(self, zone):
        if zone in self.zones:
            self.zones = sorted(self.zones.remove(zone))

    def add_node(self, node_id, node_name=None, node_zone=None):
        if node_zone not in self.zones:
            raise ValueError("Cluster not initialized with zone %s", node_zone)
        self.rings[node_zone].add_node(node_id)
        self.nodes[node_id] = node_name
        self.zone_members[node_zone].append(node_id)

    def remove_node(self, node_id, node_name=None, node_zone=None):
        if node_zone not in self.zones:
            raise ValueError("Cluster not initialized with zone %s", node_zone)
        self.rings[node_zone].remove_node(node_id)
        del self.nodes[node_id]
        self.zone_members[node_zone].remove(node_id)

    def node_name_by_id(self, node_id):
        return self.nodes[node_id]

    def find_nodes(self, product_id, block_index):
        nodes = []
        offset = int(product_id) + int(block_index) % len(self.zones)
        for i in range(self.replicas):
            zone = self.zones[(i + offset) % len(self.zones)]
            ring = self.rings[zone]
            key = "%s-%s" % (product_id, block_index)
            nodes.append(ring.find_node(key))
        return nodes
