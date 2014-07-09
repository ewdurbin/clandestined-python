
v1.0.0rc1 (2014-07-08)
======================

  - `Rendezvous.find_node` breaks ties in the event of a hash collision based
     string sort of `node_id`. ~40% overhead incurred.
   - items in array supplied to `RenezvousHash.__init__` and by extension as
     `node_id` to `Cluster.new` and `Cluster.add_node` are coerced to strings.

v1.0.0b (2014-07-07)
====================

  - `Cluster.remove_zone` now raises `ValueError` on attempt to remove a
     non-existent zone.
  - `Cluster.remove_node` and `RendezvousHash.remove_node` now raise
    `ValueError` on attempt to remove  a non-existent node.
  - Support for custom hash functions retracted for 1.0.0 milestone.
  - `murmur_seed` keyword argument renamed to `seed` for `Cluster` and
    `RendezvousHash` `__init__` methods.

v1.0.0a (2014-07-06)
====================

  - Initial Release.
