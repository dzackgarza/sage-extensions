r"""Probe: which registry holds a constructed plane of T_Co after its caller drops it.

The tower of `@cached_function` registries keyed by `id(...)` is enumerated by
import, then a plane built through the row's own constructor is dropped by its
only caller and every strong holder is printed with the attribute name it sits
under.  Three specimens: a lattice nothing else names, the plane, and the
plane's inclusion arrow.
"""

import gc
import sys
import weakref

from sage_extensions.all import *  # noqa: F401,F403

MODULES = {}


def loaded(name):
    module = sys.modules.get(name)
    return module


REGISTRIES = [
    ("sage_extensions.categories._lattice", "_lattice_on_gram"),
    ("sage_extensions.categories.lattices", "_lattice_subobject_spanning"),
    ("sage_extensions.categories.lattices", "_lattice_subobject_on_basis"),
    ("sage_extensions.categories.lattice_morphisms", "_lattice_mor"),
    ("sage_extensions.categories.lattice_morphisms", "_lattice_embedding_mor"),
    ("sage_extensions.categories.lattice_morphisms", "_lattice_isometry_mor"),
    ("sage_extensions.categories.abstract_categories.mor_categories", "_category_packet"),
]


def registry_table():
    rows = []
    for module_name, attribute in REGISTRIES:
        module = loaded(module_name)
        cache = getattr(module, attribute, None)
        if cache is None:
            rows.append((f"{module_name}.{attribute}", "absent"))
            continue
        entries = getattr(cache, "cache", None)
        if entries is None:
            rows.append((f"{module_name}.{attribute}", "no .cache"))
            continue
        rows.append((f"{module_name}.{attribute}", len(entries)))
    return rows


def describe_container(container):
    """Name the object that owns `container`, and the attribute it is held in."""
    for owner in gc.get_referrers(container):
        if owner is container:
            continue
        if isinstance(owner, dict):
            continue
        if isinstance(owner, (list, tuple)):
            continue
        name = getattr(getattr(owner, "_cachedfunc", None), "__name__", None)
        if name is not None:
            return f"registry {owner._cachedfunc.__module__}.{name}"
        instance = getattr(owner, "_instance", None)
        if instance is not None:
            method = getattr(getattr(owner, "_cachedmethod", None), "_cachedfunc", None)
            return f"registry {getattr(method, '__name__', '?')} on {type(instance).__name__}"
        attributes = getattr(owner, "__dict__", None)
        if isinstance(attributes, dict):
            names = [key for key, value in attributes.items() if value is container]
            if names:
                return f"{type(owner).__name__}.{names[0]}"
        return f"{type(owner).__name__}"
    return "no owner found"


def holder_lines(obj, label, depth=0, seen=None):
    if seen is None:
        seen = set()
    lines = []
    if id(obj) in seen:
        return lines
    seen.add(id(obj))
    for referrer in gc.get_referrers(obj):
        if referrer is seen:
            continue
        if isinstance(referrer, list):
            continue
        if isinstance(referrer, dict):
            if "__name__" in referrer or "__builtins__" in referrer:
                continue
            keys = [str(key)[:60] for key in list(referrer)[:2]]
            lines.append(f"{'  ' * depth}{label} <- dict of {len(referrer)} keys {keys}: {describe_container(referrer)}")
        elif isinstance(referrer, tuple):
            lines.append(f"{'  ' * depth}{label} <- {len(referrer)}-tuple: {describe_container(referrer)}")
        else:
            lines.append(f"{'  ' * depth}{label} <- {describe_container(referrer)}")
    return lines


def specimen(build, label):
    built = build()
    reference = weakref.ref(built)
    included = None
    try:
        included = weakref.ref(built.inclusion())
    except Exception as error:  # noqa: BLE001
        included = f"no inclusion: {error}"
    del built
    gc.collect()
    survivor = reference()
    print(f"\n[probe] {label}: alive after the drop and a collection: {survivor is not None}", flush=True)
    if survivor is not None:
        for line in holder_lines(survivor, label):
            print(f"[probe] {line}", flush=True)
    if included is not None and not isinstance(included, str):
        arrow = included()
        print(f"[probe] {label}: its inclusion survives too: {arrow is not None}", flush=True)
        if arrow is not None:
            for line in holder_lines(arrow, f"{label}.inclusion"):
                print(f"[probe] {line}", flush=True)
    return survivor


print(f"[probe] module: {sys.modules['sage_extensions'].__file__}", flush=True)
print("[probe] registries before:", flush=True)
for name, size in registry_table():
    print(f"  [reg] {name}: {size}", flush=True)

specimen(lambda: Lattices(ZZ)([[2]]), "a rank-one lattice")

holder = NamedLattices.Tco
labels = tuple(holder.module_generating_set())
names = {str(label): holder.module_generator(label) for label in labels}
first_vector = holder.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
element = holder.basis_vector(0)
specimen(lambda: element, "an element of T_Co")
specimen(lambda: holder.primitive_isotropic_subobject(first_vector, names["ep"]), "a plane of T_Co")
specimen(lambda: holder.primitive_isotropic_subobject(first_vector), "a line of T_Co")

print("\n[probe] registries after:", flush=True)
for name, size in registry_table():
    print(f"  [reg] {name}: {size}", flush=True)

family = None
from sage_extensions.categories.abstract_categories.mor_categories import _MorCategoryOf

print(f"\n[probe] _MorCategoryOf._objects of every live family:", flush=True)
for candidate in gc.get_objects():
    if isinstance(candidate, _MorCategoryOf):
        print(
            f"  [family] base {type(candidate.base_category()).__name__}"
            f" role {getattr(candidate, '_role', None)!r}"
            f" _objects {len(candidate._objects)}"
            f" _resolved_endpoint_categories {len(candidate._resolved_endpoint_categories)}",
            flush=True,
        )
