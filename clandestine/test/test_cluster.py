

import unittest

from clandestine import Cluster
from clandestine._murmur3 import murmur3_32


class ClusterTestCase(unittest.TestCase):

    def test_init_no_options(self):
        cluster = Cluster()
        self.assertEqual(murmur3_32, cluster.hash_function)
        self.assertEqual(2, cluster.replicas)
        self.assertEqual({}, cluster.nodes)
        self.assertEqual([], cluster.zones)
        self.assertEqual({}, dict(cluster.zone_members))
        self.assertEqual({}, dict(cluster.rings))

    def test_init_single_zone(self):
        cluster_config = {
            '1': {},
            '2': {},
            '3': {},
        }
        cluster = Cluster(cluster_config, replicas=1)
        self.assertEqual(1, cluster.replicas)
        self.assertEqual(3, len(cluster.nodes))
        self.assertEqual(1, len(cluster.zones))
        self.assertEqual(3, len(cluster.zone_members[None]))
        self.assertEqual(1, len(cluster.rings))
        self.assertEqual(3, len(cluster.rings[None].nodes))

    def test_init_zones(self):
        cluster_config = {
            '1': {'zone': 'a'},
            '2': {'zone': 'b'},
            '3': {'zone': 'a'},
            '4': {'zone': 'b'},
            '5': {'zone': 'a'},
            '6': {'zone': 'b'},
        }
        cluster = Cluster(cluster_config)
        self.assertEqual(2, cluster.replicas)
        self.assertEqual(6, len(cluster.nodes))
        self.assertEqual(['a', 'b'], cluster.zones)
        self.assertEqual(['1', '3', '5'], sorted(cluster.zone_members['a']))
        self.assertEqual(['2', '4', '6'], sorted(cluster.zone_members['b']))
        self.assertEqual(2, len(cluster.rings))
        self.assertEqual(3, len(cluster.rings['a'].nodes))
        self.assertEqual(3, len(cluster.rings['b'].nodes))

    def test_add_zone(self):
        cluster = Cluster()
        self.assertEqual(0, len(cluster.nodes))
        self.assertEqual([], cluster.zones)
        self.assertEqual(0, len(cluster.zone_members))
        self.assertEqual(0, len(cluster.rings))

        cluster.add_zone('b')
        self.assertEqual(0, len(cluster.nodes))
        self.assertEqual(['b'], cluster.zones)
        self.assertEqual(0, len(cluster.zone_members['b']))
        self.assertEqual(0, len(cluster.rings))

        cluster.add_zone('b')
        self.assertEqual(0, len(cluster.nodes))
        self.assertEqual(['b'], cluster.zones)
        self.assertEqual(0, len(cluster.zone_members['b']))
        self.assertEqual(0, len(cluster.rings))

        cluster.add_zone('a')
        self.assertEqual(0, len(cluster.nodes))
        self.assertEqual(['a', 'b'], cluster.zones)
        self.assertEqual(0, len(cluster.zone_members['a']))
        self.assertEqual(0, len(cluster.zone_members['b']))
        self.assertEqual(0, len(cluster.rings))

    def test_add_node(self):
        cluster = Cluster()
        self.assertEqual(0, len(cluster.nodes))
        self.assertEqual([], cluster.zones)
        self.assertEqual(0, len(cluster.zone_members))
        self.assertEqual(0, len(cluster.rings))

        cluster.add_node('2', node_zone='b')
        self.assertEqual(1, len(cluster.nodes))
        self.assertEqual(['b'], cluster.zones)
        self.assertEqual(1, len(cluster.zone_members))
        self.assertEqual(['2'], sorted(cluster.zone_members['b']))
        self.assertEqual(1, len(cluster.rings))

        cluster.add_node('1', node_zone='a')
        self.assertEqual(2, len(cluster.nodes))
        self.assertEqual(['a', 'b'], cluster.zones)
        self.assertEqual(2, len(cluster.zone_members))
        self.assertEqual(['1'], sorted(cluster.zone_members['a']))
        self.assertEqual(['2'], sorted(cluster.zone_members['b']))
        self.assertEqual(2, len(cluster.rings))

        cluster.add_node('21', node_zone='b')
        self.assertEqual(3, len(cluster.nodes))
        self.assertEqual(['a', 'b'], cluster.zones)
        self.assertEqual(2, len(cluster.zone_members))
        self.assertEqual(['1'], sorted(cluster.zone_members['a']))
        self.assertEqual(['2', '21'], sorted(cluster.zone_members['b']))
        self.assertEqual(2, len(cluster.rings))

        self.assertRaises(ValueError, cluster.add_node, '21')
        self.assertRaises(ValueError, cluster.add_node, '21', None, None)
        self.assertRaises(ValueError, cluster.add_node, '21', None, 'b')

        cluster.add_node('22', node_zone='c')
        self.assertEqual(4, len(cluster.nodes))
        self.assertEqual(['a', 'b', 'c'], cluster.zones)
        self.assertEqual(3, len(cluster.zone_members))
        self.assertEqual(['1'], sorted(cluster.zone_members['a']))
        self.assertEqual(['2', '21'], sorted(cluster.zone_members['b']))
        self.assertEqual(['22'], sorted(cluster.zone_members['c']))
        self.assertEqual(3, len(cluster.rings))

    def test_remove_node(self):
        cluster_config = {
            '1': {'zone': 'a'},
            '2': {'zone': 'b'},
            '3': {'zone': 'a'},
            '4': {'zone': 'b'},
            '5': {'zone': 'c'},
            '6': {'zone': 'c'},
        }
        cluster = Cluster(cluster_config)

        cluster.remove_node('4', node_zone='b')
        self.assertEqual(5, len(cluster.nodes))
        self.assertEqual(['a', 'b', 'c'], cluster.zones)
        self.assertEqual(3, len(cluster.zone_members))
        self.assertEqual(['1', '3'], sorted(cluster.zone_members['a']))
        self.assertEqual(['2'], sorted(cluster.zone_members['b']))
        self.assertEqual(['5', '6'], sorted(cluster.zone_members['c']))
        self.assertEqual(3, len(cluster.rings))

        cluster.remove_node('2', node_zone='b')
        self.assertEqual(4, len(cluster.nodes))
        self.assertEqual(['a', 'c'], cluster.zones)
        self.assertEqual(2, len(cluster.zone_members))
        self.assertEqual(['1', '3'], sorted(cluster.zone_members['a']))
        self.assertEqual([], sorted(cluster.zone_members['b']))
        self.assertEqual(['5', '6'], sorted(cluster.zone_members['c']))
        self.assertEqual(2, len(cluster.rings))

    def test_node_name_by_id(self):
        cluster_config = {
            '1': {'name': 'node1', 'zone': 'a'},
            '2': {'name': 'node2', 'zone': 'b'},
            '3': {'name': 'node3', 'zone': 'a'},
            '4': {'name': 'node4', 'zone': 'b'},
            '5': {'name': 'node5', 'zone': 'c'},
            '6': {'name': 'node6', 'zone': 'c'},
        }
        cluster = Cluster(cluster_config)

        self.assertEqual('node1', cluster.node_name('1'))
        self.assertEqual('node2', cluster.node_name('2'))
        self.assertEqual('node3', cluster.node_name('3'))
        self.assertEqual('node4', cluster.node_name('4'))
        self.assertEqual('node5', cluster.node_name('5'))
        self.assertEqual('node6', cluster.node_name('6'))
        self.assertEqual(None, cluster.node_name('7'))

    def test_find_nodes(self):
        cluster_config = {
            '1': {'name': 'node1', 'zone': 'a'},
            '2': {'name': 'node2', 'zone': 'a'},
            '3': {'name': 'node3', 'zone': 'b'},
            '4': {'name': 'node4', 'zone': 'b'},
            '5': {'name': 'node5', 'zone': 'c'},
            '6': {'name': 'node6', 'zone': 'c'},
        }
        cluster = Cluster(cluster_config)

        self.assertEqual(['2', '3'], cluster.find_nodes('lol'))
        self.assertEqual(['6', '2'], cluster.find_nodes('wat'))
        self.assertEqual(['5', '2'], cluster.find_nodes('ok'))
        self.assertEqual(['1', '3'], cluster.find_nodes('bar'))
        self.assertEqual(['1', '3'], cluster.find_nodes('foo'))
        self.assertEqual(['2', '4'], cluster.find_nodes('slap'))

    def test_find_nodes_by_index(self):
        cluster_config = {
            '1': {'name': 'node1', 'zone': 'a'},
            '2': {'name': 'node2', 'zone': 'a'},
            '3': {'name': 'node3', 'zone': 'b'},
            '4': {'name': 'node4', 'zone': 'b'},
            '5': {'name': 'node5', 'zone': 'c'},
            '6': {'name': 'node6', 'zone': 'c'},
        }
        cluster = Cluster(cluster_config)

        self.assertEqual(['6', '1'], cluster.find_nodes_by_index(1, 1))
        self.assertEqual(['2', '4'], cluster.find_nodes_by_index(1, 2))
        self.assertEqual(['4', '5'], cluster.find_nodes_by_index(1, 3))
        self.assertEqual(['1', '4'], cluster.find_nodes_by_index(2, 1))
        self.assertEqual(['3', '5'], cluster.find_nodes_by_index(2, 2))
        self.assertEqual(['5', '2'], cluster.find_nodes_by_index(2, 3))


class ClusterIntegrationTestCase(unittest.TestCase):

    def test_grow(self):
        cluster_config = {
            '1': {'name': 'node1', 'zone': 'a'},
            '2': {'name': 'node2', 'zone': 'a'},
            '3': {'name': 'node3', 'zone': 'b'},
            '4': {'name': 'node4', 'zone': 'b'},
            '5': {'name': 'node5', 'zone': 'c'},
            '6': {'name': 'node6', 'zone': 'c'},
        }
        cluster = Cluster(cluster_config)

        placements = {}
        for i in cluster.nodes:
            placements[i] = []
        for i in range(1000):
            nodes = cluster.find_nodes(str(i))
            for node in nodes:
                placements[node].append(i)

        cluster.add_node('7', node_name='node7', node_zone='a')
        cluster.add_node('8', node_name='node8', node_zone='b')
        cluster.add_node('9', node_name='node9', node_zone='c')

        new_placements = {}
        for i in cluster.nodes:
            new_placements[i] = []
        for i in range(1000):
            nodes = cluster.find_nodes(str(i))
            for node in nodes:
                new_placements[node].append(i)

        keys = [k for sublist in placements.values() for k in sublist]
        new_keys = [k for sublist in new_placements.values() for k in sublist]
        self.assertEqual(sorted(keys), sorted(new_keys))

        added = 0
        removed = 0
        for node, assignments in new_placements.items():
            after = set(assignments)
            before = set(placements.get(node, []))
            removed += len(before.difference(after))
            added += len(after.difference(before))

        self.assertEqual(added, removed)
        self.assertEqual(1384, (added + removed))

    def test_shrink(self):
        cluster_config = {
            '1': {'name': 'node1', 'zone': 'a'},
            '2': {'name': 'node2', 'zone': 'a'},
            '3': {'name': 'node3', 'zone': 'b'},
            '4': {'name': 'node4', 'zone': 'b'},
            '5': {'name': 'node5', 'zone': 'c'},
            '6': {'name': 'node6', 'zone': 'c'},
            '7': {'name': 'node7', 'zone': 'a'},
            '8': {'name': 'node8', 'zone': 'a'},
            '9': {'name': 'node9', 'zone': 'b'},
            '10': {'name': 'node10', 'zone': 'b'},
            '11': {'name': 'node11', 'zone': 'c'},
            '12': {'name': 'node12', 'zone': 'c'},
        }
        cluster = Cluster(cluster_config)

        placements = {}
        for i in cluster.nodes:
            placements[i] = []
        for i in range(10000):
            nodes = cluster.find_nodes(str(i))
            for node in nodes:
                placements[node].append(i)

        cluster.remove_node('7', node_name='node7', node_zone='a')
        cluster.remove_node('9', node_name='node9', node_zone='b')
        cluster.remove_node('11', node_name='node11', node_zone='c')

        new_placements = {}
        for i in cluster.nodes:
            new_placements[i] = []
        for i in range(10000):
            nodes = cluster.find_nodes(str(i))
            for node in nodes:
                new_placements[node].append(i)

        keys = [k for sublist in placements.values() for k in sublist]
        new_keys = [k for sublist in new_placements.values() for k in sublist]
        self.assertEqual(sorted(keys), sorted(new_keys))

        added = 0
        removed = 0
        for node, assignments in placements.items():
            after = set(assignments)
            before = set(new_placements.get(node, []))
            removed += len(before.difference(after))
            added += len(after.difference(before))

        self.assertEqual(added, removed)
        self.assertEqual(9804, (added + removed))

    def test_add_zone(self):
        cluster_config = {
            '1': {'name': 'node1', 'zone': 'a'},
            '2': {'name': 'node2', 'zone': 'a'},
            '3': {'name': 'node3', 'zone': 'b'},
            '4': {'name': 'node4', 'zone': 'b'},
        }
        cluster = Cluster(cluster_config)

        placements = {}
        for i in cluster.nodes:
            placements[i] = []
        for i in range(1000):
            nodes = cluster.find_nodes(str(i))
            for node in nodes:
                placements[node].append(i)

        cluster.add_node('5', node_name='node5', node_zone='c')
        cluster.add_node('6', node_name='node6', node_zone='c')

        new_placements = {}
        for i in cluster.nodes:
            new_placements[i] = []
        for i in range(1000):
            nodes = cluster.find_nodes(str(i))
            for node in nodes:
                new_placements[node].append(i)

        keys = [k for sublist in placements.values() for k in sublist]
        new_keys = [k for sublist in new_placements.values() for k in sublist]
        self.assertEqual(sorted(keys), sorted(new_keys))

        added = 0
        removed = 0
        for node, assignments in new_placements.items():
            after = set(assignments)
            before = set(placements.get(node, []))
            removed += len(before.difference(after))
            added += len(after.difference(before))

        self.assertEqual(added, removed)
        self.assertEqual(1332, (added + removed))

    def test_remove_zone(self):
        cluster_config = {
            '1': {'name': 'node1', 'zone': 'a'},
            '2': {'name': 'node2', 'zone': 'a'},
            '3': {'name': 'node3', 'zone': 'b'},
            '4': {'name': 'node4', 'zone': 'b'},
            '5': {'name': 'node5', 'zone': 'c'},
            '6': {'name': 'node6', 'zone': 'c'},
            '7': {'name': 'node7', 'zone': 'a'},
            '8': {'name': 'node8', 'zone': 'a'},
            '9': {'name': 'node9', 'zone': 'b'},
            '10': {'name': 'node10', 'zone': 'b'},
            '11': {'name': 'node11', 'zone': 'c'},
            '12': {'name': 'node12', 'zone': 'c'},
        }
        cluster = Cluster(cluster_config)

        placements = {}
        for i in cluster.nodes:
            placements[i] = []
        for i in range(10000):
            nodes = cluster.find_nodes(str(i))
            for node in nodes:
                placements[node].append(i)

        cluster.remove_node('5', node_name='node5', node_zone='c')
        cluster.remove_node('6', node_name='node6', node_zone='c')
        cluster.remove_node('11', node_name='node11', node_zone='c')
        cluster.remove_node('12', node_name='node12', node_zone='c')

        new_placements = {}
        for i in cluster.nodes:
            new_placements[i] = []
        for i in range(10000):
            nodes = cluster.find_nodes(str(i))
            for node in nodes:
                new_placements[node].append(i)

        keys = [k for sublist in placements.values() for k in sublist]
        new_keys = [k for sublist in new_placements.values() for k in sublist]
        self.assertEqual(sorted(keys), sorted(new_keys))

        added = 0
        removed = 0
        for node, assignments in placements.items():
            after = set(assignments)
            before = set(new_placements.get(node, []))
            removed += len(before.difference(after))
            added += len(after.difference(before))

        self.assertEqual(added, removed)
        self.assertEqual(13332, (added + removed))

if __name__ == '__main__':
    unittest.main()
