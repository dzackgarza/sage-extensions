"""Price the three terms of the kernel plane row: the split gathered, the split
dropped as it is consumed, and the contract step's rebuild-and-read.

The row's own shape is ``gather``: `_plane_orbit_from_parabolic_stabilizer`
appends every transported plane of the split to a list and returns the tuple,
so the planes are all retained before the first cusp is made.  ``drop`` is the
same loop with the plane released once its cusp exists -- what the cusp row
needs, since a cusp keeps a span.  ``contract`` is the driver's per-cusp line,
`_coordinates(cusp.representative())`.  One mode a process.
"""

import os
import sys
import time

sys.path.insert(0, "/repos/sage-extensions/tests")

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import _arithmetic_cusp
from sage_extensions.categories.orthogonal_quotients import (
    _composite_divided_class_action,
)

from coble_gamma_co_2_incidence_rows import _coordinates

MODE = os.environ.get("PROBE_MODE", "gather")
PLANES = int(os.environ.get("PROBE_PLANES", "1000"))
BAND = int(os.environ.get("PROBE_BAND", "100"))
start = time.monotonic()
clock = lambda: time.monotonic() - start  # noqa: E731


def rss_kib():
    return int(open("/proc/self/status").read().split("VmRSS:")[1].split()[0])


def mark(what):
    print(f"[{clock():9.1f} s rss {rss_kib() / 1024:8.1f} MiB] {what}", flush=True)


lattice = NamedLattices.Tco
labels = tuple(lattice.module_generating_set())
names = {str(label): lattice.module_generator(label) for label in labels}
first_vector = lattice.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
source = lattice.primitive_isotropic_subobject(first_vector, names["ep"])
subgroup = lattice.stable_orthogonal_group()
quotient = subgroup.finite_character_quotient()
family = tuple(source.parabolic_stabilizer_generators())
mark(f"T_Co, Otilde(T_Co), {len(family)} parabolic generators, mode {MODE}")

identity = quotient._discriminant_group.one()
splittings = quotient._iter_splitting_isometries_in_im_rho(family)
transversal = time.monotonic()
lift, element = next(splittings)
mark(f"the transversal (the finite image's whole coset walk) {time.monotonic() - transversal:.1f} s")
quotient.register_isotropic_lift(source, quotient.supergroup.one(), family, identity)

before = rss_kib()
cusps = []
planes = []
times = []
for position in range(PLANES):
    t0 = time.monotonic()
    splitting, discriminant_image = next(splittings)
    transported = splitting.transport_isotropic_object(source)
    quotient.register_isotropic_lift(transported, splitting, family, discriminant_image)
    t1 = time.monotonic()
    cusp = _arithmetic_cusp(subgroup, transported)
    t2 = time.monotonic()
    cusps.append(cusp)
    if MODE == "gather":
        planes.append(transported)
    else:
        del transported
    times.append((t1 - t0, t2 - t1))
    if position and position % BAND == 0:
        share = (rss_kib() - before) / position
        print(
            f"[{clock():9.1f} s rss {rss_kib() / 1024:8.1f} MiB] {MODE} {position}/{PLANES}: "
            f"{share:.1f} KiB a plane so far",
            flush=True,
        )
after = rss_kib()
mark(f"{MODE}: {len(cusps)} planes and cusps, {len(planes)} planes held")

mean = lambda pairs, field: 1000 * sum(pair[field] for pair in pairs) / len(pairs)  # noqa: E731
first, last = times[:BAND], times[-BAND:]
print(f"\n[{MODE}], {len(times)} planes")
print(f"  the split's step and the transport: {mean(times, 0):.3f} ms a plane")
print(f"  the cusp (span key):                {mean(times, 1):.3f} ms a plane")
print(f"  both: {mean([(a + b, 0) for a, b in times], 0):.3f} ms a plane")
print(
    f"  first {BAND}: {mean(first, 0) + mean(first, 1):.3f} ms   "
    f"last {BAND}: {mean(last, 0) + mean(last, 1):.3f} ms a plane"
)
print(
    f"  resident: {before / 1024:.1f} MiB -> {after / 1024:.1f} MiB, "
    f"{(after - before) / len(times):.1f} KiB a plane"
)
print(
    f"  at 189720 planes: {189720 * (after - before) / len(times) / 1024 / 1024:.2f} GiB "
    f"on top of {before / 1024 / 1024:.2f} GiB, "
    f"{189720 * (sum(a + b for a, b in times) / len(times)) / 3600:.2f} h of planes"
)

if MODE == "contract":
    before = rss_kib()
    rows = []
    for position, cusp in enumerate(cusps):
        t0 = time.monotonic()
        representative = cusp.representative()
        t1 = time.monotonic()
        _coordinates(representative)
        t2 = time.monotonic()
        del representative
        rows.append((t1 - t0, t2 - t1))
        if position and position % BAND == 0:
            share = (rss_kib() - before) / position
            print(
                f"[{clock():9.1f} s rss {rss_kib() / 1024:8.1f} MiB] contract "
                f"{position}/{len(cusps)}: {share:.1f} KiB a plane so far",
                flush=True,
            )
    after = rss_kib()
    first, last = rows[:BAND], rows[-BAND:]
    print(f"\n[the contract step], {len(rows)} plane cusps")
    print(f"  rebuild representative(): {mean(rows, 0):.3f} ms a plane")
    print(f"  read _coordinates():      {mean(rows, 1):.3f} ms a plane")
    print(f"  both:                     {mean([(a + b, 0) for a, b in rows], 0):.3f} ms a plane")
    print(
        f"  first {BAND}: {mean(first, 0) + mean(first, 1):.3f} ms   "
        f"last {BAND}: {mean(last, 0) + mean(last, 1):.3f} ms a plane"
    )
    print(
        f"  resident: {before / 1024:.1f} MiB -> {after / 1024:.1f} MiB, "
        f"{(after - before) / len(rows):.1f} KiB a plane"
    )
    print(
        f"  at 189720 cusps: {189720 * (sum(a + b for a, b in rows) / len(rows)):.0f} s "
        f"and {189720 * (after - before) / len(rows) / 1024 / 1024:.2f} GiB"
    )
mark("done")
