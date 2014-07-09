import sys
import unittest

import clandestined
from clandestined import RendezvousHash
from clandestined import Cluster

def mock_murmur3_32(key, seed=0):
    return 4294967295

class CollisionTestCase(unittest.TestCase):

    def setUp(self):
        self.original_murmur3_32 = clandestined._murmur3.murmur3_32
        clandestined._murmur3.murmur3_32 = mock_murmur3_32

    def tearDown(self):
        clandestined._murmur3.murmur3_32 = self.original_murmur3_32

    def test_monkey_patch(self):
        rendezvous = RendezvousHash()
        self.assertEqual(rendezvous.hash_function('lol'), 4294967295)
        self.assertEqual(rendezvous.hash_function('wat'), 4294967295)

    def test_rendezvous_collision(self):
        nodes = ['c', 'b', 'a']
        rendezvous = RendezvousHash(nodes)
        for i in range(1000):
            self.assertEqual('c', rendezvous.find_node(i))

    def test_rendezvous_names(self):
        nodes = [1, 2, 3, 'a', 'b', 'lol.wat.com']
        rendezvous = RendezvousHash(nodes)
        for i in range(10):
            self.assertEqual('lol.wat.com', rendezvous.find_node(i))
        nodes = [1, 'a', '0']
        rendezvous = RendezvousHash(nodes)
        for i in range(10):
            self.assertEqual('a', rendezvous.find_node(i))

    def test_cluster_collision(self):
        nodes = {'1': {'zone': 'a'}, '2': {'zone': 'a'},
                 '3': {'zone': 'b'}, '4': {'zone': 'b'}}
        cluster = Cluster(nodes)
        for n in range(100):
            for m in range(100):
                self.assertEqual(['2', '4'], sorted(cluster.find_nodes_by_index(n, m)))

if __name__ == "__main__":
    unittest.main()
