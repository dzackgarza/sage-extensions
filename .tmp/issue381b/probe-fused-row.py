"""One kernel plane row as one stream: the walk, the plane's cusp, its edges, its lift spent.

The row is not built and then read.  The walk yields a plane, the plane's cusp is
made from it, the divided-class relation decides that plane's edges from the
covering the row has carried so far, and the plane's registered lift is released
by the relation itself -- so what is resident is the cusp row, the edge records
and the planes held between two yields, not the 189720 lifts the split would
otherwise register before the relation starts.

The row's anchor is pinned by the source's span, for the reason
`probe-resume.py` records: a drawn representative is not reproduced by a second
process, and a walk of another anchor is another row.
"""

import os
import sys
import time

sys.path.insert(0, "/repos/sage-extensions/tests")

from sage_extensions.all import *  # noqa: F401,F403
import sage_extensions.categories.isotropic_orbits as isotropic_orbits  # noqa: E402
import sage_extensions.categories.orthogonal_quotients as orthogonal_quotients  # noqa: E402
from sage_extensions.categories.sets.finite_ordered_sets import (  # noqa: E402
    _distinct_finite_ordered_set,
)

from coble_gamma_co_2_incidence_rows import (  # noqa: E402
    _lattice_by_name,
    _row_subgroup,
    chosen_route,
    row_contract,
)

ROW = os.environ.get("PROBE_ROW", "Otilde")
LATTICE_NAME = os.environ.get("PROBE_LATTICE", "Tco")
EVERY = int(os.environ.get("PROBE_EVERY", "10000"))
start = time.monotonic()
clock = lambda: time.monotonic() - start  # noqa: E731


def mark(what):
    rss = int(open("/proc/self/status").read().split("VmRSS:")[1].split()[0]) / 1024
    print(f"[{clock():9.1f} s rss {rss:8.1f} MiB] {what}", flush=True)


lattice = _lattice_by_name(LATTICE_NAME)
subgroup = _row_subgroup(lattice, ROW)
quotient = subgroup.finite_character_quotient()
drawn = tuple(lattice.Aut().isotropic_orbit_representatives(2))[0]
source = isotropic_orbits._subobject_of_span(lattice, isotropic_orbits._span_key(drawn))
family = tuple(source.parabolic_stabilizer_generators())
mark(f"{LATTICE_NAME}, the {ROW} row, {len(family)} parabolic generators, source span "
     f"{isotropic_orbits._span_key(source)[1]}")

lines = tuple(subgroup.cusps(1))
mark(f"the line row: {len(lines)} line cusps")


def plane_cusps():
    r"""The row's plane cusps, made one at a time from the walk that transports them."""
    for position, plane in enumerate(
        orthogonal_quotients._iter_transported_planes(quotient, source, family)
    ):
        if position % EVERY == 0:
            mark(f"the walk: {position} planes reached")
        yield isotropic_orbits._arithmetic_cusp(subgroup, plane)


cusps = []
incidences = []
for position, (cusp, edges) in enumerate(
    subgroup.divided_class_incidence_of_planes(plane_cusps())
):
    cusps.append(cusp)
    incidences.extend(edges)
    if position % EVERY == 0 and position:
        mark(f"the fused row: {position} planes, {len(incidences)} edges")
mark(f"the row decided: {len(cusps)} plane cusps, {len(incidences)} edges")

subgroup.cusps.clear_cache()
subgroup.cusps.set_cache(_distinct_finite_ordered_set(cusps), 2)
mark(f"the cusp row seeded: {subgroup.cusps(2).cardinality()} plane cusps")
taken, reason = chosen_route(subgroup, "divided-class")
planes_row = tuple(subgroup.cusps(2))
outcome = row_contract(lattice, subgroup, ROW, lines, planes_row, tuple(incidences), taken)
mark(f"the verdict: {outcome.report()}")
