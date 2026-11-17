r"""Probe: the live path from the ambient lattice to a dropped isotropic subobject.

Builds one plane of ``U + U(2) + <-2>``, drops it, collects, and follows
``gc.get_referrers`` upward from the surviving plane, naming at each step the
cached function or the cached-method caller that owns the dictionary the object
sits in, and stopping at the lattice.  A reference cycle alone would not survive
``gc.collect()``, so what this prints is a path from a live root.
"""

import gc
import weakref

from sage_extensions.all import *  # noqa: F401,F403

SEEN = set()


def describe(owner):
    name = getattr(getattr(owner, "_cachedfunc", None), "__name__", None)
    if name is not None:
        return f"cached function {getattr(owner._cachedfunc, '__module__', '?')}.{name}"
    instance = getattr(owner, "_instance", None)
    if instance is not None:
        cname = getattr(getattr(owner, "_cachedmethod", None), "_cachedfunc", None)
        cname = getattr(cname, "__name__", "?")
        return f"cached method {cname} on {type(instance).__name__}"
    return f"{type(owner).__name__}: {repr(owner)[:100]}"


def walk(obj, depth, path=""):
    if depth < 0 or id(obj) in SEEN or len(SEEN) > 60:
        return
    SEEN.add(id(obj))
    for referrer in gc.get_referrers(obj):
        if id(referrer) in SEEN:
            continue
        if isinstance(referrer, dict):
            if "__name__" in referrer or "__builtins__" in referrer:
                continue
            owners = [
                owner
                for owner in gc.get_referrers(referrer)
                if not isinstance(owner, list) and owner is not referrer
            ]
            for owner in owners[:3]:
                if isinstance(owner, dict):
                    continue
                print(f"{'  ' * (3 - depth)}-> {describe(owner)}  [{path}]", flush=True)
                walk(owner, depth - 1, path + "/dict")
        elif isinstance(referrer, list):
            continue
        else:
            print(f"{'  ' * (3 - depth)}-> {describe(referrer)}", flush=True)
            walk(referrer, depth - 1, path)


lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
plane = lattice.primitive_isotropic_subobject(lattice.basis_vector(0), lattice.basis_vector(2))
reference = weakref.ref(plane)
del plane
gc.collect()
survivor = reference()
print(f"[probe] alive after the drop and a collection: {survivor is not None}", flush=True)
if survivor is not None:
    print(f"[probe] the lattice is {describe(lattice)}", flush=True)
    walk(survivor, 3)
