r"""Probe: the marginal bytes of the two things an edge certificate retains.

The record of #381 derives the certificate coefficient -- "three certificates a
plane, each retaining a flag and its two transporters" -- and does not read it,
because the ``T_Co`` row never returned.  Its two parts are measurable without
the row: a *carried* flag, which is what ``transport_covering`` makes at every
plane (``move.transport_isotropic_object(flag)``), and a *fresh transporter*,
which is a product in the ambient generating family.  Both are made here on
``T_Co`` from the same objects the walk makes them from.
"""
import gc
import os
import sys
import time

START = time.monotonic()
MAXDEPTH = 14


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
from sage_extensions.categories.isotropic_orbits import FlagType

lattice = NamedLattices.Tco
labels = tuple(lattice.module_generating_set())
names = {str(label): lattice.module_generator(label) for label in labels}
first = lattice.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
plane = lattice.primitive_isotropic_subobject(first, names["ep"])
subgroup = lattice.stable_orthogonal_group()
ambient = subgroup.supergroup()
generators = tuple(ambient.group_generators())
print(f"[{time.monotonic() - START:.1f} s] row objects, {len(generators)} ambient generators,"
      f" rss {rss_mib():.1f} MiB", flush=True)

inclusion = plane.inclusion()
domain = inclusion.domain()
basis = tuple(inclusion(domain.module_generator(label)) for label in domain.module_generating_set())
flag = lattice.isotropic_flag(basis[0], basis[1], flag_type=FlagType((1, 2)))
print(f"  the plane's own flag: terms {tuple(term.module_rank() for term in flag.terms())}",
      flush=True)

seed = (lattice, subgroup, ambient, plane, *generators)
meter = Meter()
for shared in seed:
    meter.walk(shared)
print(f"  seeded {len(meter.seen)} shared objects", flush=True)

moves = (
    ("one generator", generators[0]),
    ("a product of two", generators[0] * generators[1]),
    ("a product of five", generators[0] * generators[1] * generators[2] * generators[3] * generators[4]),
)
# One meter across the three: the first carried flag pays whatever the refined
# isotropic category costs to build once, and the later ones are the steady
# per-flag cost the row pays at every plane.
for label, move in moves:
    element_bytes = meter.walk(move)
    carried = move.transport_isotropic_object(flag)
    carried_bytes = meter.walk(carried)
    plane_bytes = meter.walk(carried.terms()[1])
    line_bytes = meter.walk(carried.terms()[0])
    print(
        f"  {label:18s}: transporter {element_bytes:7d} B; the flag it carries {carried_bytes:7d} B"
        f" (plane term {plane_bytes} B, line term {line_bytes} B)",
        flush=True,
    )

print("\n[probe] one certificate retains a carried flag and two transporters; three a plane.",
      flush=True)
