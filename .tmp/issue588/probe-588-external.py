r"""Probe: the external roots of a dropped object's own reference cycle.

`gc.get_referents` is what the collector sees, so a node the collector cannot
traverse is one it cannot free.  The closure from the survivor is walked, and
every object outside that closure which the collector sees pointing into it is
printed: those are the edges that keep the object alive.
"""

import gc
import os
import sys
import weakref

from sage_extensions.all import *  # noqa: F401,F403


def closure_of(root):
    seen = {id(root): root}
    frontier = [root]
    while frontier:
        following = []
        for item in frontier:
            for referent in gc.get_referents(item):
                if id(referent) not in seen:
                    seen[id(referent)] = referent
                    following.append(referent)
        frontier = following
    return seen


def describe(obj):
    if isinstance(obj, dict):
        names = [key for key in list(obj)[:40] if isinstance(key, str)]
        return f"dict({len(obj)}) attrs={names[:4]}"
    if isinstance(obj, (list, tuple, set, frozenset)):
        return f"{type(obj).__name__}({len(obj)})"
    module = getattr(type(obj), "__module__", "")
    name = getattr(getattr(obj, "_cachedfunc", None), "__name__", None)
    if name is not None:
        return f"registry {obj._cachedfunc.__module__}.{name}"
    return f"{type(obj).__name__[:50]} of {module[:40]}: {str(obj)[:50]!r}"


def external_roots(survivor, label):
    closure = closure_of(survivor)
    inside = set(closure)
    print(f"[probe] {label}: its own closure holds {len(inside)} objects", flush=True)
    parents = {}
    for obj in gc.get_objects():
        if id(obj) in inside:
            continue
        for referent in gc.get_referents(obj):
            if id(referent) in inside:
                parents.setdefault(id(obj), obj)
    print(f"[probe] {label}: external objects the collector sees pointing in: {len(parents)}", flush=True)
    for obj in list(parents.values())[:40]:
        target = [describe(referent) for referent in gc.get_referents(obj) if id(referent) in inside][:2]
        print(f"  [external] {describe(obj)} -> {target}", flush=True)


holder = NamedLattices.Tco
labels = tuple(holder.module_generating_set())
names = {str(label): holder.module_generator(label) for label in labels}
first_vector = holder.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
if os.environ.get("SPECIMEN") == "lattice":
    specimen = Lattices(ZZ)([[2]])
    label = "a rank-one lattice"
else:
    specimen = holder.primitive_isotropic_subobject(first_vector, names["ep"])
    label = "a plane of T_Co"
reference = weakref.ref(specimen)
del specimen
gc.collect()
survivor = reference()
print(f"[probe] {label}: alive after the drop {survivor is not None}", flush=True)
if survivor is not None:
    external_roots(survivor, label)
