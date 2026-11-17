r"""Probe: what one retained isometry of O(T_Co) holds, attribute by attribute.

An isometry is the one object ``register_isotropic_lift`` keeps per plane beside
the span key.  This measures its marginal bytes and attributes them to its own
first-level attributes, so the report can say which part of the retained lift is
the matrix and which is the morphism machinery around it.
"""
import gc
import os
import sys
import time

MAXDEPTH = 14
START = time.monotonic()


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


class Meter:
    def __init__(self):
        self.seen = set()

    def walk(self, obj, depth=0):
        if depth > MAXDEPTH:
            return 0
        oid = id(obj)
        if oid in self.seen:
            return 0
        self.seen.add(oid)
        total = sys.getsizeof(obj)
        if isinstance(obj, (int, float, bool, str, bytes, complex, type(None), type)):
            return total
        try:
            referents = gc.get_referents(obj)
        except TypeError:
            return total
        for child in referents:
            total += self.walk(child, depth + 1)
        return total


from sage_extensions.all import *  # noqa: F401,F403

lattice = NamedLattices.Tco
subgroup = lattice.stable_orthogonal_group()
ambient = subgroup.supergroup()
generators = tuple(ambient.group_generators())
print(f"[{time.monotonic() - START:.1f} s] ambient group, {len(generators)} generators,"
      f" rss {rss_mib():.1f} MiB", flush=True)

meter = Meter()
for shared in (lattice, subgroup, ambient, *generators):
    meter.walk(shared)
print(f"  seeded {len(meter.seen)} shared objects", flush=True)

for label, element in (
    ("one generator", generators[0]),
    ("a product of two", generators[0] * generators[1]),
    ("a product of five", generators[0] * generators[1] * generators[2] * generators[3] * generators[4]),
):
    fresh = Meter()
    fresh.seen = set(meter.seen)
    attributes = getattr(element, "__dict__", None)
    parts = {}
    if isinstance(attributes, dict):
        for key in sorted(attributes):
            parts[key] = fresh.walk(attributes[key])
    shell = fresh.walk(element)
    total = sum(parts.values()) + shell
    print(f"\n{label}: marginal {total} B; getsizeof {sys.getsizeof(element)};"
          f" shell and attribute dict {shell} B", flush=True)
    for key, size in sorted(parts.items(), key=lambda item: -item[1]):
        print(f"    .{key:38s} {size:8d} B", flush=True)
    matrix = None
    for name in ("forward", "_matrix", "matrix"):
        if hasattr(element, name):
            try:
                matrix = getattr(element, name)
                break
            except Exception:
                continue
print(f"\n[done] rss {rss_mib():.1f} MiB", flush=True)
