r"""Probe: what one transported flag costs the lattice, on a lattice whose rows return at once.

The carry's per-plane work builds a carried flag for each flag of the covering, and
an ``IsotropicFlag`` asks the lattice for its terms through
``primitive_isotropic_subobject`` -- a ``cached_method`` on the lattice, keyed by
the spanning family.  This probe transports one flag of ``U + U(2) + <-2>`` by a
growing family of isometries and prints, after each transport, the entry count and
the shallow size of that constructor's cache and the resident set, so the
retention is a number in bytes per transported flag.  It also reads the three
facts any replacement of that cache has to respect: whether the elements key it
by value or by identity, whether the subobject is weakly referenceable, and
whether an equal family built independently answers the same object.
"""

import gc
import os
import sys
import time
import weakref

START = time.monotonic()
TRANSPORTS = int(os.environ.get("PROBE_TRANSPORTS", "40"))

CACHE = "_cache__primitive_isotropic_subobject"


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import FlagType


def shallow(value):
    total = sys.getsizeof(value, 0)
    for key, item in value.items():
        total += sys.getsizeof(key, 0) + sys.getsizeof(item, 0)
        if isinstance(key, tuple):
            total += sum(sys.getsizeof(part, 0) for part in key)
    return total


def retained(lattice):
    cache = vars(lattice).get(CACHE, {})
    return len(cache), shallow(cache) / 1024


lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
print(f"[probe] {lattice}, rank {lattice.module_rank()}", flush=True)
adapters = [lattice.basis_vector(position) for position in range(lattice.module_rank())]
gram = [[lattice.b(adapters[a], adapters[b]) for b in range(lattice.module_rank())] for a in range(lattice.module_rank())]
print(f"[probe] the adapted Gram matrix: {gram}", flush=True)
line_vector = adapters[0]
plane_vector = adapters[2]
print(f"[probe] squares {lattice.b(line_vector, line_vector)} and {lattice.b(plane_vector, plane_vector)},"
      f" pairing {lattice.b(line_vector, plane_vector)}", flush=True)

plane = lattice.primitive_isotropic_subobject(line_vector, plane_vector)
print(f"[probe] the plane: rank {plane.module_rank()}, retained {retained(lattice)}", flush=True)

# (i) Are the elements a value key or an identity key?
copies = [lattice.basis_vector(position) for position in range(lattice.module_rank())]
try:
    hashes = (hash(copies[0]) == hash(line_vector), hash(copies[0]))
except TypeError as error:
    hashes = (f"unhashable: {error}", None)
print(f"[probe] two basis vectors of one position agree: {copies[0] == line_vector};"
      f" the same objects: {copies[0] is line_vector};"
      f" equal hashes: {hashes[0]}", flush=True)
before = retained(lattice)
again = lattice.primitive_isotropic_subobject(copies[0], copies[2])
print(f"[probe] an equal family built independently answers the same object: {again is plane};"
      f" retained before {before} after {retained(lattice)}", flush=True)

# (ii) Is a subobject weakly referenceable, and does a dropped one die by refcount?
probe_plane = lattice.primitive_isotropic_subobject(copies[0], copies[2])
reference = weakref.ref(probe_plane)
del probe_plane
print(f"[probe] a dropped subobject with no other holder is alive: {reference() is not None};"
      f" retained {retained(lattice)}", flush=True)
gc.collect()
print(f"[probe] after a collection: alive {reference() is not None}, retained {retained(lattice)}", flush=True)

# (iii) One transported flag each, by the powers of one isometry.
subgroup = lattice.stable_orthogonal_group()
generators = tuple(subgroup.group_generators())
print(f"[probe] O(L) generators: {len(generators)}", flush=True)
flag = lattice.isotropic_flag(line_vector, plane_vector, flag_type=FlagType((1, 2)))
print(f"[probe] the flag's terms retain {retained(lattice)}", flush=True)
move = subgroup.one()
start_count, start_size = retained(lattice)
start_rss = rss_mib()
for step in range(TRANSPORTS):
    move = move * generators[step % len(generators)]
    carried = move.transport_isotropic_object(flag)
    count, size = retained(lattice)
    print(
        f"  [transport {step + 1:5d}] retained {count:6d} subobjects, {size:9.1f} KiB"
        f"  rss {rss_mib():8.1f} MiB  {(size - start_size) / (step + 1):8.2f} KiB a transport",
        flush=True,
    )
    del carried
print(
    f"[probe] RESULT transports={TRANSPORTS} retained {start_count} -> {retained(lattice)[0]} subobjects,"
    f" {start_size:.1f} -> {retained(lattice)[1]:.1f} KiB,"
    f" rss {start_rss:.1f} -> {rss_mib():.1f} MiB, wall {time.monotonic() - START:.1f} s",
    flush=True,
)
