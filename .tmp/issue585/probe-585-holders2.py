r"""Probe: which cache keeps a dropped isotropic subobject alive, named by its owner.

Builds one plane of ``U + U(2) + <-2>``, drops it, and follows the referrers two
steps: the surviving plane's referrers, and, for each dictionary among them, the
objects that hold that dictionary -- a ``cached_function`` names itself by its
wrapped function, and anything else by its type and a short representation.
"""

import gc
import weakref

from sage_extensions.all import *  # noqa: F401,F403


def describe(owner):
    r"""A short name for the object holding a cache dictionary."""
    name = getattr(getattr(owner, "_cachedfunc", None), "__name__", None)
    if name is not None:
        module = getattr(owner._cachedfunc, "__module__", "?")
        return f"cached function {module}.{name}"
    return f"{type(owner).__name__}: {repr(owner)[:120]}"


lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
plane = lattice.primitive_isotropic_subobject(lattice.basis_vector(0), lattice.basis_vector(2))
reference = weakref.ref(plane)
del plane
gc.collect()
survivor = reference()
print(f"[probe] after the drop the plane is alive: {survivor is not None}", flush=True)
for referrer in gc.get_referrers(survivor):
    if not isinstance(referrer, dict):
        continue
    if "__name__" in referrer or "__builtins__" in referrer:
        continue
    keys = [str(key)[:80] for key in list(referrer.keys())[:3]]
    print(f"[probe] a dict holding it, keys {keys}", flush=True)
    for owner in gc.get_referrers(referrer):
        print(f"    held by {describe(owner)}", flush=True)
