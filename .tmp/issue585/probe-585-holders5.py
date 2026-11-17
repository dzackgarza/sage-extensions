r"""Probe: every container that holds a dropped isotropic subobject, and what holds each of them.

Builds one plane of ``U + U(2) + <-2>``, drops it, collects, and then scans the
heap for the objects whose own ``__dict__`` holds the survivor -- that is, the
morphism-set tower built around it -- and, for each, prints the cache or the
object whose own ``__dict__`` holds *that*.  Two levels is enough to name the
registry that is the root.
"""

import gc
import weakref

from sage_extensions.all import *  # noqa: F401,F403
from sage.structure.sage_object import SageObject


def describe(owner):
    name = getattr(getattr(owner, "_cachedfunc", None), "__name__", None)
    if name is not None:
        return f"cached function {getattr(owner._cachedfunc, '__module__', '?')}.{name}"
    instance = getattr(owner, "_instance", None)
    if instance is not None:
        wrapped = getattr(getattr(owner, "_cachedmethod", None), "_cachedfunc", None)
        return f"cached method {getattr(wrapped, '__name__', '?')} on {type(instance).__name__}"
    return f"{type(owner).__name__}: {repr(owner)[:90]}"


def owners_of(target, limit=4):
    found = []
    for referrer in gc.get_referrers(target):
        if isinstance(referrer, list):
            continue
        if isinstance(referrer, dict):
            if "__name__" in referrer or "__builtins__" in referrer:
                continue
            for owner in gc.get_referrers(referrer):
                if isinstance(owner, (list, dict)) or owner is referrer:
                    continue
                found.append(f"{describe(owner)}  (in a dict)")
                if len(found) >= limit:
                    return found
        else:
            found.append(describe(referrer))
            if len(found) >= limit:
                return found
    return found


lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
plane = lattice.primitive_isotropic_subobject(lattice.basis_vector(0), lattice.basis_vector(2))
reference = weakref.ref(plane)
del plane
gc.collect()
survivor = reference()
print(f"[probe] alive after the drop and a collection: {survivor is not None}", flush=True)
if survivor is None:
    raise SystemExit(0)
holders = []
for candidate in gc.get_objects():
    if not isinstance(candidate, SageObject):
        continue
    try:
        state = object.__getattribute__(candidate, "__dict__")
    except (AttributeError, TypeError):
        continue
    if any(value is survivor for value in state.values()):
        holders.append(candidate)
print(f"[probe] {len(holders)} objects hold it in their own __dict__", flush=True)
for holder in holders:
    print(f"[holder] {describe(holder)}", flush=True)
    for line in owners_of(holder):
        print(f"    held by {line}", flush=True)
