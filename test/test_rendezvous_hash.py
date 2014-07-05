
import unittest

from clandestine import RendezvousHash
from murmur3 import murmur3_x86_32


class RendezvousHashTestCase(unittest.TestCase):

    def test_init_no_options(self):
        rendezvous = RendezvousHash()
        self.assertEqual(0, len(rendezvous.nodes))
        self.assertEqual(murmur3_x86_32, rendezvous.hash_function)

    def test_init(self):
        nodes = ['0', '1', '2']
        rendezvous = RendezvousHash(nodes=nodes)
        self.assertEqual(3, len(rendezvous.nodes))
        self.assertEqual(murmur3_x86_32, rendezvous.hash_function)

    def test_add_node(self):
        rendezvous = RendezvousHash()
        rendezvous.add_node('1')
        self.assertEqual(1, len(rendezvous.nodes))
        rendezvous.add_node('1')
        self.assertEqual(1, len(rendezvous.nodes))
        rendezvous.add_node('2')
        self.assertEqual(2, len(rendezvous.nodes))
        rendezvous.add_node('1')
        self.assertEqual(2, len(rendezvous.nodes))

    def test_remove_node(self):
        nodes = ['0', '1', '2']
        rendezvous = RendezvousHash(nodes=nodes)
        rendezvous.remove_node('2')
        self.assertEqual(2, len(rendezvous.nodes))
        rendezvous.remove_node('2')
        self.assertEqual(2, len(rendezvous.nodes))
        rendezvous.remove_node('1')
        self.assertEqual(1, len(rendezvous.nodes))
        rendezvous.remove_node('0')
        self.assertEqual(0, len(rendezvous.nodes))

    def test_find_node(self):
        nodes = ['0', '1', '2']
        rendezvous = RendezvousHash(nodes=nodes)
        self.assertEqual('0', rendezvous.find_node('ok'))
        self.assertEqual('1', rendezvous.find_node('mykey'))
        self.assertEqual('2', rendezvous.find_node('wat'))

    def test_find_node_after_removal(self):
        nodes = ['0', '1', '2']
        rendezvous = RendezvousHash(nodes=nodes)
        rendezvous.remove_node('1')
        self.assertEqual('0', rendezvous.find_node('ok'))
        self.assertEqual('0', rendezvous.find_node('mykey'))
        self.assertEqual('2', rendezvous.find_node('wat'))

    def test_find_node_after_addition(self):
        nodes = ['0', '1', '2']
        rendezvous = RendezvousHash(nodes=nodes)
        self.assertEqual('0', rendezvous.find_node('ok'))
        self.assertEqual('1', rendezvous.find_node('mykey'))
        self.assertEqual('2', rendezvous.find_node('wat'))
        self.assertEqual('2', rendezvous.find_node('lol'))
        rendezvous.add_node('3')
        self.assertEqual('0', rendezvous.find_node('ok'))
        self.assertEqual('1', rendezvous.find_node('mykey'))
        self.assertEqual('2', rendezvous.find_node('wat'))
        self.assertEqual('3', rendezvous.find_node('lol'))


class RendezvousHashIntegrationTestCase(unittest.TestCase):

    def test_grow(self):
        rendezvous = RendezvousHash()

        placements = {}
        for i in range(10):
            rendezvous.add_node(str(i))
            placements[str(i)] = []
        for i in range(1000):
            node = rendezvous.find_node(str(i))
            placements[node].append(i)

        new_placements = {}
        for i in range(20):
            rendezvous.add_node(str(i))
            new_placements[str(i)] = []
        for i in range(1000):
            node = rendezvous.find_node(str(i))
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
        self.assertEqual(1062, (added + removed))

    def test_shrink(self):
        rendezvous = RendezvousHash()

        placements = {}
        for i in range(10):
            rendezvous.add_node(str(i))
            placements[str(i)] = []
        for i in range(1000):
            node = rendezvous.find_node(str(i))
            placements[node].append(i)

        rendezvous.remove_node('9')
        new_placements = {}
        for i in range(9):
            new_placements[str(i)] = []
        for i in range(1000):
            node = rendezvous.find_node(str(i))
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
        self.assertEqual(202, (added + removed))

if __name__ == '__main__':
    unittest.main()
