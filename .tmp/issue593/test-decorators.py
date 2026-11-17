import gc, sys
sys.path.insert(0, "src")
from sage_extensions.utilities import (
    _address_registry, _instance_address_registry, _weak_address_registry,
)

built = []

@_address_registry
def build(subject):
    built.append(id(subject))
    return "record for " + subject.name

class Shell:
    __slots__ = ("name",)
    def __init__(self, name):
        self.name = name

one = Shell("first")
first = build(one)
assert build(one) is first, "a live subject answers its recorded answer"
assert len(built) == 1
address = id(one)
del one, first
replacement = Shell("second")
print("address reused:", id(replacement) == address)
answer = build(replacement)
print("answered:", answer)
assert answer.subject is replacement, "a question about a new object is computed again"

# instance registry
calls = []

class Owner:
    @_instance_address_registry
    def view(self, partner):
        calls.append(partner)
        return (self, partner)

a, b = Owner(), Owner()
p = Shell("p")
va = a.view(p)
assert a.view(p) is va
assert b.view(p) is not va, "each instance has its own table"
assert len(calls) == 2
del p
q = Shell("q")
a.view(q)
assert calls[-1] is q, "a new partner is computed again"

# weak registry
@_weak_address_registry
def weak_build(subject):
    return Shell("weak")

s = Shell("s")
answer = weak_build(s)
assert weak_build(s) is answer
del answer
gc.collect()
assert weak_build(s) is not None
print("ok")
