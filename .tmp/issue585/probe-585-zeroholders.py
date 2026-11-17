r"""Probe: what holds the zero subobject of a lattice after its caller has dropped it.

The zero subobject is the smallest Parent the library constructs: no basis, no
relation to any other object.  If it survives a drop and a collection, the
holder this prints is the mechanism that keeps every constructed Parent, and that
is what a row's per-plane retention would have to beat.
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


lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
zero = lattice.primitive_isotropic_subobject()
reference = weakref.ref(zero)
del zero
gc.collect()
survivor = reference()
print(f"[probe] the zero subobject is alive after the drop: {survivor is not None}", flush=True)
if survivor is None:
    raise SystemExit(0)
print(f"[probe] its class: {type(survivor).__name__}", flush=True)
for referrer in gc.get_referrers(survivor):
    if isinstance(referrer, list):
        continue
    if isinstance(referrer, dict):
        if "__name__" in referrer or "__builtins__" in referrer:
            continue
        print(f"[probe] a dict holds it, keys {[str(key)[:60] for key in list(referrer)[:3]]}", flush=True)
        for owner in gc.get_referrers(referrer):
            if isinstance(owner, (list, dict)) or owner is referrer:
                continue
            print(f"    held by {describe(owner)}", flush=True)
    else:
        print(f"[probe] held by {describe(referrer)}", flush=True)
