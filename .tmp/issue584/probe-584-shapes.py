"""Probe: the shapes and sizes of one registered lift of Otilde(T_Co).

Cheap: no split walk.  Builds the row's objects, registers one plane's lift, and
prints what the registry entry holds -- the span key, the lift element and the
parabolic family tuple -- with sys.getsizeof broken down by attribute and a
referents traversal that reports a marginal (shared-cancelling) size.
"""
import gc
import os
import sys
import time

START = time.monotonic()


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


def deep(obj, seen, depth=0, maxdepth=14):
    if depth > maxdepth:
        return 0
    oid = id(obj)
    if oid in seen:
        return 0
    seen.add(oid)
    total = sys.getsizeof(obj)
    if isinstance(obj, (int, float, bool, str, bytes, complex, type(None), type)):
        return total
    try:
        referents = gc.get_referents(obj)
    except Exception:
        return total
    for child in referents:
        total += deep(child, seen, depth + 1, maxdepth)
    return total


def dump(label, obj, seen, maxdepth=14, show_attrs=True):
    size = deep(obj, seen, maxdepth=maxdepth)
    print(f"  {label}: {type(obj).__module__}.{type(obj).__name__} "
          f"getsizeof={sys.getsizeof(obj)} marginal={size} B", flush=True)
    attributes = getattr(obj, "__dict__", None)
    if show_attrs and isinstance(attributes, dict):
        for key, value in attributes.items():
            fresh = set(seen)
            attribute_size = sys.getsizeof(value) if not isinstance(value, (dict, list, tuple, set)) else deep(value, fresh, 0, maxdepth)
            print(f"      .{key}: {type(value).__name__} getsizeof={sys.getsizeof(value)} "
                  f"deep~{attribute_size}", flush=True)
    return size


from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import _span_key

print(f"[start] rss {rss_mib():.1f} MiB", flush=True)
lattice = NamedLattices.Tco
labels = tuple(lattice.module_generating_set())
names = {str(label): lattice.module_generator(label) for label in labels}
first = lattice.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
plane = lattice.primitive_isotropic_subobject(first, names["ep"])
subgroup = lattice.stable_orthogonal_group()
quotient = subgroup.finite_character_quotient()
print(f"[{time.monotonic() - START:.1f}s] row objects, rss {rss_mib():.1f} MiB", flush=True)
print(f"  plane is parabolic complete: {plane.is_parabolic_complete()}", flush=True)
family = tuple(plane.parabolic_stabilizer_generators())
print(f"[{time.monotonic() - START:.1f}s] the family: {len(family)} generators, "
      f"rss {rss_mib():.1f} MiB", flush=True)

ambient = subgroup.supergroup()
print(f"  ambient group: {type(ambient).__module__}.{type(ambient).__name__}", flush=True)
identity = ambient.one()
print(f"  identity: {type(identity).__module__}.{type(identity).__name__}", flush=True)
generators = tuple(ambient.group_generators())
lift = generators[0]
print(f"  one ambient generator: {type(lift).__module__}.{type(lift).__name__}", flush=True)

transported = lift.transport_isotropic_object(plane)
print(f"  one transported plane: {type(transported).__module__}.{type(transported).__name__}",
      flush=True)
span = _span_key(transported)
print(f"  span key: {type(span).__name__} of {len(span)} entries: "
      f"{str(span)[:200]}", flush=True)

print("\n[1] the family tuple", flush=True)
seen = set()
print(f"  getsizeof(tuple) = {sys.getsizeof(family)}; "
      f"items shared with the plane's own family: "
      f"{all(a is b for a, b in zip(family, tuple(plane.parabolic_stabilizer_generators())))}",
      flush=True)
family_ids = {id(g) for g in family}
dump("  family[0] (one generator)", family[0], set(), maxdepth=8)

print("\n[2] the lift element", flush=True)
seen_lift = set()
dump("  lift", lift, seen_lift, maxdepth=10)

print("\n[3] the transported plane", flush=True)
seen_plane = set()
dump("  transported", transported, seen_plane, maxdepth=10)

print("\n[4] the registry entry", flush=True)
quotient.register_isotropic_lift(plane, identity, family)
registry = quotient.__dict__["_isotropic_lift_registry"]
print(f"  registry: {len(registry)} entries, getsizeof {sys.getsizeof(registry)}", flush=True)
key, value = next(iter(registry.items()))
print(f"  key getsizeof {sys.getsizeof(key)}; value getsizeof {sys.getsizeof(value)}; "
      f"value[0] {type(value[0]).__name__}; value[1] tuple of {len(value[1])}", flush=True)

print("\n[5] the quotient's whole __dict__ after one registration", flush=True)
for name, value in quotient.__dict__.items():
    if isinstance(value, dict):
        detail = f"dict of {len(value)}"
    elif isinstance(value, (list, tuple, set)):
        detail = f"{type(value).__name__} of {len(value)}"
    else:
        detail = type(value).__name__
    print(f"  {name}: {detail}", flush=True)

print("\n[6] caches: cached_method attributes on the quotient", flush=True)
for name in sorted(quotient.__dict__):
    if name.startswith("_cache__") or "cache" in name.lower():
        value = quotient.__dict__[name]
        print(f"  {name}: {type(value).__name__} len {len(value) if hasattr(value, '__len__') else '?'}",
              flush=True)

print(f"\n[done] rss {rss_mib():.1f} MiB, wall {time.monotonic() - START:.1f} s", flush=True)
