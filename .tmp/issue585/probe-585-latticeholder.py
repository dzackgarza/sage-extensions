r"""Probe: what holds a lattice whose caller has dropped it.

The smallest specimen: one rank-one lattice, built and dropped, with nothing else
naming it.  Its holders are the registries that make a constructed Parent of this
library permanent; an element is the control, since an element is released.
"""

import gc
import weakref

from sage_extensions.all import *  # noqa: F401,F403


def describe(owner):
    name = getattr(getattr(owner, "_cachedfunc", None), "__name__", None)
    if name is not None:
        return f"cached function {getattr(owner._cachedfunc, '__module__', '?')}.{name}"
    instance = getattr(owner, "_instance", None)
    if instance is not None:
        wrapped = getattr(getattr(owner, "_cachedmethod", None), "_cachedfunc", None)
        return f"cached method {getattr(wrapped, '__name__', '?')} on {type(instance).__name__}"
    return f"{type(owner).__name__}: {repr(owner)[:90]}"


released = {}
lattice = Lattices(ZZ)([[2]])
reference = weakref.ref(lattice)
del lattice
gc.collect()
survivor = reference()
print(f"[probe] a rank-one lattice is alive after the drop: {survivor is not None}", flush=True)
if survivor is not None:
    for referrer in gc.get_referrers(survivor):
        if isinstance(referrer, list):
            continue
        if isinstance(referrer, dict):
            if "__name__" in referrer or "__builtins__" in referrer:
                continue
            print(f"[probe] a dict holds it, keys {[str(key)[:70] for key in list(referrer)[:3]]}", flush=True)
            for owner in gc.get_referrers(referrer):
                if isinstance(owner, (list, dict)) or owner is referrer:
                    continue
                print(f"    held by {describe(owner)}", flush=True)
        else:
            print(f"[probe] held by {describe(referrer)}", flush=True)
