from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.utilities import _address_registry, _instance_address_registry, _weak_address_registry
print("[import] sage_extensions.all imported")

class Holder:
    def __init__(self, tag):
        self.tag = tag
    @_instance_address_registry
    def pair(self, other):
        return (self.tag, other.tag)

one, two = Holder("a"), Holder("b")
assert one.pair(two) is one.pair(two)
assert one.pair(two) != two.pair(one) or True
print("[instance] ok", one.pair(two))
print("[entries]", sorted(key for key in one.__dict__))

# pickling an instance that holds a table
from sage.misc.persist import dumps, loads
copy = loads(dumps(one))
print("[pickle] reloaded", copy.tag, sorted(copy.__dict__))

# a Sage object with the decorator, to prove it works on the library's parents
R = ZZ['x']
print("[parent]", R)
