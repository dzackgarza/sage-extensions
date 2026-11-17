r"""Probe: every registry in the process, and whether it holds a dropped plane of T_Co.

The plane is built through the row's own constructor, its only caller drops it,
and every `CachedFunction`, every cached-method store on an owned object and
every attribute dict of an owned category object is then asked whether the plane
is reachable from its entries within a small depth.
"""

import gc
import sys
import weakref

from sage_extensions.all import *  # noqa: F401,F403

DEPTH = 6


def owned(obj):
    module = getattr(type(obj), "__module__", "")
    return isinstance(module, str) and module.startswith("sage_extensions")


def attribute_dict(obj):
    if not owned(obj):
        return None
    try:
        attributes = object.__getattribute__(obj, "__dict__")
    except AttributeError:
        return None
    return attributes if isinstance(attributes, dict) else None


def descendable(value):
    return isinstance(value, (dict, list, tuple, set, frozenset)) or owned(value)


def values_of(item):
    if isinstance(item, dict):
        return (*item.keys(), *item.values())
    if isinstance(item, (list, tuple, set, frozenset)):
        return item
    attributes = attribute_dict(item)
    return attributes.values() if attributes else ()


def reachable(container, target, depth=DEPTH):
    frontier = [container]
    seen = {id(container)}
    for _ in range(depth):
        following = []
        for item in frontier:
            for value in values_of(item):
                if value is target:
                    return True
                if descendable(value) and id(value) not in seen:
                    seen.add(id(value))
                    following.append(value)
        frontier = following
        if not frontier:
            return False
    return False


def name_of_function(function):
    module = getattr(function, "__module__", "?")
    name = getattr(function, "__qualname__", None) or getattr(function, "__name__", "?")
    return f"{module}.{name}"


def key_shape(sample):
    parts = sample if isinstance(sample, tuple) else (sample,)
    return f"{len(parts)} parts {[type(part).__name__ for part in parts]}"


def registry_rows(target, label):
    rows = []
    from sage.misc.cachefunc import CachedFunction

    for obj in gc.get_objects():
        if not isinstance(obj, CachedFunction):
            continue
        entries = getattr(obj, "cache", None)
        if not isinstance(entries, dict) or not entries:
            continue
        if reachable(entries, target):
            rows.append(
                (
                    f"cached_function {name_of_function(getattr(obj, 'f', None))}"
                    f" (cache {type(entries).__name__})",
                    f"{len(entries)} entries, key {key_shape(next(iter(entries)))}",
                )
            )
    for obj in gc.get_objects():
        attributes = attribute_dict(obj)
        if not attributes:
            continue
        for attribute, value in list(attributes.items()):
            if attribute.startswith("_cache__") and isinstance(value, dict) and value:
                if reachable(value, target):
                    rows.append(
                        (
                            f"cached_method {attribute} on {type(obj).__name__[:44]}",
                            f"{len(value)} entries, key {key_shape(next(iter(value)))}",
                        )
                    )
            elif isinstance(value, dict) and value:
                if reachable(value, target, depth=3):
                    rows.append(
                        (
                            f"attribute store {type(obj).__name__[:44]}.{attribute}",
                            f"{len(value)} entries",
                        )
                    )
    print(f"\n[probe] registries holding {label}:", flush=True)
    if not rows:
        print("  [none]", flush=True)
    for registry, detail in rows:
        print(f"  [holds] {registry}: {detail}", flush=True)
    return rows


holder = NamedLattices.Tco
labels = tuple(holder.module_generating_set())
names = {str(label): holder.module_generator(label) for label in labels}
first_vector = holder.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
import os

if os.environ.get("SPECIMEN") == "lattice":
    plane = Lattices(ZZ)([[2]])
    arrow = plane
else:
    plane = holder.primitive_isotropic_subobject(first_vector, names["ep"])
    arrow = plane.inclusion()
plane_reference = weakref.ref(plane)
arrow_reference = weakref.ref(arrow)
del plane
del arrow
gc.collect()
plane_survivor = plane_reference()
arrow_survivor = arrow_reference()
print(f"[probe] the plane is alive after the drop: {plane_survivor is not None}", flush=True)
print(f"[probe] its inclusion is alive after the drop: {arrow_survivor is not None}", flush=True)
if plane_survivor is not None:
    registry_rows(plane_survivor, "the plane")
if arrow_survivor is not None:
    registry_rows(arrow_survivor, "the plane's inclusion arrow")
