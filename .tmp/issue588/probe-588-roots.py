r"""Probe: the strong roots of a dropped plane of T_Co, two edges at a time.

Every referrer is named by the attribute it sits under, and a registry entry is
followed to the object that owns the registry so the root is visible.
"""

import gc
import sys
import weakref

from sage_extensions.all import *  # noqa: F401,F403

SKIP_TYPES = (list, frame_type) if (frame_type := type(sys._getframe())) else (list,)


def owner_name(container):
    found = []
    for owner in gc.get_referrers(container):
        if owner is container or isinstance(owner, (dict, list, tuple)):
            continue
        name = getattr(getattr(owner, "_cachedfunc", None), "__name__", None)
        if name is not None:
            found.append(f"registry {owner._cachedfunc.__module__}.{name}")
            continue
        instance = getattr(owner, "_instance", None)
        if instance is not None:
            method = getattr(getattr(owner, "_cachedmethod", None), "_cachedfunc", None)
            found.append(f"registry {getattr(method, '__name__', '?')} on {type(instance).__name__}")
            continue
        found.append(type(owner).__name__[:60])
    return found or ["?"]


def describe(referrer):
    if isinstance(referrer, dict):
        keys = list(referrer)[:3]
        shape = [str(key)[:40] for key in keys if not isinstance(key, str)]
        attributes = [key for key in keys if isinstance(key, str)]
        return f"dict({len(referrer)}) attrs={attributes[:3]} keys={shape} owned by {owner_name(referrer)}"
    if isinstance(referrer, tuple):
        return f"tuple({len(referrer)}) owned by {owner_name(referrer)}"
    return f"{type(referrer).__name__}: {str(referrer)[:60]!r}"


def walk(obj, label, depth=2, seen=None, path=""):
    if seen is None:
        seen = set()
    for referrer in gc.get_referrers(obj):
        if isinstance(referrer, SKIP_TYPES):
            continue
        if isinstance(referrer, dict) and ("__builtins__" in referrer or "__name__" in referrer):
            continue
        if id(referrer) in seen:
            continue
        seen.add(id(referrer))
        line = f"{path}<- {describe(referrer)}"
        print(f"[probe]   {label}: {line}", flush=True)
        if depth > 1 and not isinstance(referrer, (dict, tuple)):
            walk(referrer, label, depth - 1, seen, path + "  ")


holder = NamedLattices.Tco
labels = tuple(holder.module_generating_set())
names = {str(label): holder.module_generator(label) for label in labels}
first_vector = holder.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
plane = holder.primitive_isotropic_subobject(first_vector, names["ep"])
reference = weakref.ref(plane)
del plane
gc.collect()
survivor = reference()
print(f"[probe] alive after the drop: {survivor is not None}", flush=True)
if survivor is not None:
    walk(survivor, "plane", depth=2)
