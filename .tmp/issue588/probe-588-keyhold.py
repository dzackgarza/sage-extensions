r"""Probe: does a weak-valued registry still hold its object through its key?

A `weak_cached_function` holds its value weakly and its key strongly.  A key
built from the value's own datum -- the Gram tensor, the span basis -- therefore
keeps the object alive however weak the value is.  Each registry in the tower is
asked, for a dropped specimen, whether the specimen is a key component, a value,
or reachable from the key.
"""

import gc
import os
import sys
import weakref

from sage_extensions.all import *  # noqa: F401,F403

import sage_extensions.categories._lattice as lattice_module
import sage_extensions.categories.lattices as lattices_module
import sage_extensions.categories.lattice_morphisms as morphisms_module

REGISTRIES = (
    ("_lattice_on_gram", lattice_module),
    ("_lattice_subobject_spanning", lattices_module),
    ("_primitive_isotropic_subobject", lattices_module),
    ("_lattice_mor", morphisms_module),
    ("_lattice_embedding_mor", morphisms_module),
    ("_lattice_isometry_mor", morphisms_module),
)


def parts(key):
    return key if isinstance(key, tuple) else (key,)


def reachable(container, target, depth=3):
    frontier = [container]
    seen = {id(container)}
    for _ in range(depth):
        following = []
        for item in frontier:
            values = (
                (*item.keys(), *item.values())
                if isinstance(item, dict)
                else item
                if isinstance(item, (list, tuple, set, frozenset))
                else ()
            )
            for value in values:
                if value is target:
                    return True
                if isinstance(value, (dict, list, tuple, set, frozenset)):
                    if id(value) not in seen:
                        seen.add(id(value))
                        following.append(value)
        frontier = following
    return False


def report(specimen, label):
    print(f"\n[probe] {label}:", flush=True)
    for name, module in REGISTRIES:
        registry = getattr(module, name, None)
        if registry is None:
            continue
        entries = getattr(registry, "cache", None)
        if entries is None:
            continue
        as_key = [key for key in entries if any(part is specimen for part in parts(key))]
        from_key = [key for key in entries if any(reachable(part, specimen, 2) for part in parts(key))]
        as_value = [key for key, value in entries.items() if value is specimen]
        print(
            f"  [reg] {name}: {len(entries)} entries, cache {type(entries).__name__},"
            f" specimen as key component {len(as_key)}, reachable from a key {len(from_key)},"
            f" as value {len(as_value)}",
            flush=True,
        )
        for key in from_key[:2]:
            marks = [
                f"{type(part).__name__}{'*' if part is specimen else ''}"
                f"{'/dir' if reachable(part, specimen, 2) else ''}"
                for part in parts(key)
            ]
            print(f"        key {marks}", flush=True)


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
    report(survivor, label)
