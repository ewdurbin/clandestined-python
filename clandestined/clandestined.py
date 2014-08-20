
from collections import defaultdict

from . import _murmur3


class RendezvousHash(object):

    def __init__(self, nodes=None, seed=0):
        self.nodes = []
        self.seed = seed
        if nodes is not None:
            self.nodes = nodes
        self.hash_function = lambda x: _murmur3.murmur3_32(x, seed)

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)

    def remove_node(self, node):
        if node in self.nodes:
            self.nodes.remove(node)
        else:
            raise ValueError("No such node %s to remove" % (node))

    def find_node(self, key):
        high_score = -1
        winner = None
        for node in self.nodes:
            score = self.hash_function("%s-%s" % (str(node), str(key)))
            if score > high_score:
                (high_score, winner) = (score, node)
            elif score == high_score:
                (high_score, winner) = (score, max(str(node), str(winner)))
        return winner


class Cluster(object):

    def __init__(self, cluster_config=None, replicas=2, seed=0):
        self.seed = seed

        def RendezvousHashConstructor():
            return RendezvousHash(nodes=None, seed=self.seed)

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
        else:
            raise ValueError("No such zone %s to remove" % (zone))

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
        nodes = set()
        if offset is None:
            offset = sum(ord(char) for char in key) % len(self.zones)
        for i in range(self.replicas):
            zone = self.zones[(i + offset) % len(self.zones)]
            ring = self.rings[zone]
            nodes.add(ring.find_node(key))
        return list(nodes)

    def find_nodes_by_index(self, partition_id, key_index):
        offset = int(partition_id) + int(key_index) % len(self.zones)
        key = "%s-%s" % (partition_id, key_index)
        return self.find_nodes(key, offset=offset)
