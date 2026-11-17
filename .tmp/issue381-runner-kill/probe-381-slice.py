r"""Probe: #381's kernel incidence row on a slice of its plane row.

The dispatched row is ``subgroup.tits_building_incidence()`` for
``Otilde(T_Co) = ker rho``.  Its phases are: the line row, the ambient flag
row, the plane row (189720 cusps, the split of the plane's parabolic) and the
walk that carries the covering of one plane to every other plane and makes one
certificate per endpoint pair.  This probe runs the same phases in the same
order on the same objects, stopping the plane row at PROBE_PLANES planes, and
records wall time and RSS at every phase and inside the walk at every plane.

Two departures from the dispatched call, both forced by the time this probe
may take, and both stated in the report:

* the ambient flag row ``O(T_Co).isotropic_orbit_representatives(2,
  flag=True)`` is not recomputed here.  ``O(T_Co)`` has one orbit of
  primitive isotropic flags over ``T_Co`` (the ambient incidence is one edge),
  so one flag built from the slicing plane's own adapted basis is a
  representative of that row, and it is patched in place of the row.  The row
  is a fixed cost of the dispatched call and not a per-plane cost.
* the driver's contract check on the returned relation is not run: it is one
  pass over the returned certificates, and this probe measures the call.

The plane row's own route is the one ``_plane_orbit_from_parabolic_stabilizer``
takes -- the plane's certified parabolic, the split of its cosets in the
finite image, and one registered lift per representative -- cut off after
PROBE_PLANES representatives.  The cusp row is then cached under
``subgroup.cusps(2)``, so the public call reads the slice as its plane row.
"""

import os
import sys
import threading
import time
import traceback

START = time.monotonic()
PLANES = int(os.environ.get("PROBE_PLANES", "10"))
PHASE = os.environ.get("PROBE_PHASE", "row")
SHOW_STACKS = [True]
MAIN = threading.get_ident()


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


def sample():
    while True:
        time.sleep(10.0)
        line = f"[rss] t={time.monotonic() - START:7.1f}s rss={rss_mib():8.1f} MiB"
        if SHOW_STACKS[0]:
            frame = sys._current_frames().get(MAIN)
            if frame is not None:
                tail = traceback.extract_stack(frame)[-4:]
                line += "  at " + " <- ".join(
                    f"{os.path.basename(entry.filename)}:{entry.lineno}:{entry.name}" for entry in tail
                )
        print(line, flush=True)


threading.Thread(target=sample, daemon=True).start()

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import FlagType, _arithmetic_cusp
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

MARK = time.monotonic()


def stage(label):
    global MARK
    now = time.monotonic()
    print(f"    {now - MARK:9.2f} s  {label}  rss {rss_mib():8.1f} MiB", flush=True)
    MARK = now


def coordinates(subobject):
    inclusion = subobject.inclusion()
    domain = inclusion.domain()
    lattice = inclusion.codomain()
    labels = tuple(lattice.module_generating_set())
    return tuple(
        tuple(int(inclusion(domain.module_generator(label)).to_vector()(other)) for other in labels)
        for label in domain.module_generating_set()
    )


class TimedRow:
    r"""A cusp row that reports the time a consumer spends on each cusp."""

    def __init__(self, cusps):
        self._cusps = tuple(cusps)
        self._passes = 0

    def __iter__(self):
        self._passes += 1
        passage = self._passes
        mark = time.monotonic()
        for position, cusp in enumerate(self._cusps):
            yield cusp
            now = time.monotonic()
            print(
                f"  [row pass {passage} plane {position + 1:6d}/{len(self._cusps)}]"
                f" {now - mark:9.3f} s  rss {rss_mib():8.1f} MiB",
                flush=True,
            )
            mark = now

    def __len__(self):
        return len(self._cusps)

    def __repr__(self):
        return f"a slice of {len(self._cusps)} plane cusps"


lattice = NamedLattices.Tco
labels = tuple(lattice.module_generating_set())
names = {str(label): lattice.module_generator(label) for label in labels}
first = lattice.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
plane = lattice.primitive_isotropic_subobject(first, names["ep"])
print(f"[probe] {PLANES} planes of the row; the slicing plane {coordinates(plane)}", flush=True)
stage("T_Co and the row's plane")

subgroup = lattice.stable_orthogonal_group()
quotient = subgroup.finite_character_quotient()
stage("Otilde and its character quotient")

line_cusps = None
if PHASE == "walk":
    line_cusps = subgroup.cusps(1)
    stage(f"the line row: {int(line_cusps.cardinality())} cusps")

print(f"[probe] the slicing plane is parabolic complete: {plane.is_parabolic_complete()}", flush=True)
family = tuple(plane.parabolic_stabilizer_generators())
stage(f"the plane's parabolic: {len(family)} generators")
quotient.register_isotropic_lift(plane, quotient.supergroup.one(), family)

# The plane row's own route, cut off after PLANES representatives: one coset of
# the finite image at a time, the lift it was reached by, and the plane that
# lift places the source plane at.
representatives = []
splittings = quotient._iter_splitting_isometries_in_im_rho(family)
carried = next(splittings)
stage("the split's first lift")
mark = time.monotonic()
for position in range(PLANES):
    splitting = carried if position == 0 else next(splittings)
    transported = splitting.transport_isotropic_object(plane)
    quotient.register_isotropic_lift(transported, splitting, family)
    representatives.append(transported)
    band = max(1, PLANES // 10)
    if position < 10 or (position + 1) % band == 0 or position + 1 == PLANES:
        now = time.monotonic()
        steps = 1 if position == 0 else min(band, position)
        print(
            f"  [split plane {position + 1:6d}/{PLANES}] {now - mark:9.4f} s over {steps} steps"
            f"  ({1000 * (now - mark) / steps:8.3f} ms a plane)"
            f"  rss {rss_mib():8.1f} MiB"
            f"  lifts {len(quotient.__dict__.get('_isotropic_lift_registry', {}))}",
            flush=True,
        )
        mark = now
stage(f"the plane row's first {len(representatives)} planes")

if PHASE == "row":
    print(
        f"[probe] RESULT phase=row planes={len(representatives)} wall={time.monotonic() - START:.1f} s"
        f" rss={rss_mib():.1f} MiB lifts={len(quotient.__dict__.get('_isotropic_lift_registry', {}))}",
        flush=True,
    )
    raise SystemExit(0)

plane_cusps = tuple(_arithmetic_cusp(subgroup, representative) for representative in representatives)
stage(f"{len(plane_cusps)} plane cusps")
subgroup.cusps.set_cache(TimedRow(plane_cusps), 2)
print(f"[probe] the cached plane row answers {len(subgroup.cusps(2))} cusps", flush=True)

# One flag of the ambient flag row, built from this plane's own adapted basis
# and patched in place of the row: O(T_Co) has one orbit of these flags.
inclusion = plane.inclusion()
domain = inclusion.domain()
basis = tuple(domain.module_generating_set())
vectors = tuple(inclusion(domain.module_generator(label)) for label in basis)
ambient_flag = lattice.isotropic_flag(vectors[0], vectors[1], flag_type=FlagType((1, 2)))


def ambient_flag_row(rank, *, flag=False, _held=(ambient_flag,)):
    return finite_ordered_set(_held) if flag else finite_ordered_set((plane,))


ambient = subgroup.supergroup()
ambient.isotropic_orbit_representatives = ambient_flag_row
assert ambient.isotropic_orbit_representatives is ambient_flag_row
print(f"[probe] the ambient flag row is one flag: {ambient_flag}", flush=True)
stage("the ambient flag row")

SHOW_STACKS[0] = True
began = time.monotonic()
incidences = tuple(subgroup.tits_building_incidence())
elapsed = time.monotonic() - began
SHOW_STACKS[0] = False
stage(f"the incidence call returned {len(incidences)} certificates in {elapsed:.1f} s")
print(
    f"[probe] retained after the walk: lifts {len(quotient.__dict__.get('_isotropic_lift_registry', {}))},"
    f" coverings {len(quotient.__dict__.get('_isotropic_covering_registry', {}))},"
    f" transports {int(quotient.retained_isotropic_transport_count())}",
    flush=True,
)
print(
    f"[probe] RESULT planes={len(plane_cusps)} edges={len(incidences)}"
    f" line_cusps={int(line_cusps.cardinality())} wall={time.monotonic() - START:.1f} s"
    f" rss={rss_mib():.1f} MiB",
    flush=True,
)
