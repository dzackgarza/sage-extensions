r"""Probe: `Otilde(T_Co)`'s rank-2 cusp row against its own length.

The row is built here from the statements the library makes for it, so that a
prefix of it can be built at all: the route's own iterator
(``_yield_subgroup_isotropic_orbit_representatives``) materializes the whole
189720-plane row before it yields (``_plane_orbit_from_parabolic_stabilizer``
collects its ``representatives``), so its first ``next`` is the whole row and
no slice of it exists.  What is timed, per plane, is exactly what that walk
does per plane:

* ``next(splittings)`` -- the split's walk, ``_iter_splitting_isometries_in_im_rho``,
  which materializes its transversal on the first draw;
* ``lift.transport_isotropic_object(source)`` and ``register_isotropic_lift``;
* ``_arithmetic_cusp(subgroup, plane)`` -- the span key (a row Hermite form) and
  the cusp object, which is what ``cusps(2)`` keeps a plane as.

Then the ingress the row ends with: ``finite_ordered_set(tuple(cusps))`` timed
whole, and the insertion the ingress is, banded inside one process -- a cusp's
hash is constant over its universe (``_ArithmeticCuspEngine.__hash__``), so
every insertion compares against every point already in the bucket.

Nothing here asserts a value: the probe reports times, and the row's length is
its input.
"""

import gc
import os
import time
from time import perf_counter

START = perf_counter()
WALL_START = time.monotonic()
PLANES = int(os.environ.get("PROBE_PLANES", "1000"))
BAND = int(os.environ.get("PROBE_BAND", "100"))
INGRESS = os.environ.get("PROBE_INGRESS", "1") == "1"
PREFIXES = tuple(int(entry) for entry in os.environ.get("PROBE_PREFIXES", "200,400,800").split(","))
PAIRS = int(os.environ.get("PROBE_PAIRS", "0"))
LIBRARY = int(os.environ.get("PROBE_LIBRARY", "0"))
PROFILE = int(os.environ.get("PROBE_PROFILE", "0"))


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


def say(label):
    print(f"[{perf_counter() - START:9.1f} s rss {rss_mib():8.1f} MiB] {label}", flush=True)


from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import _arithmetic_cusp
from sage_extensions.categories.orthogonal_quotients import (
    _composite_divided_class_action,
)
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

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
say(f"T_Co rank {lattice.module_rank()}, Otilde(T_Co), its character quotient, {len(family)} parabolic generators")

identity_element = quotient._discriminant_group.one()
splittings = quotient._iter_splitting_isometries_in_im_rho(family)
t = perf_counter()
lift, element = next(splittings)
walk = perf_counter() - t
quotient.register_isotropic_lift(source, quotient.supergroup.one(), family, identity_element)
say(f"the split's first lift (the finite image's whole coset walk) {walk:.1f} s")

t = perf_counter()
row = [_arithmetic_cusp(subgroup, source)]
source_cusp = perf_counter() - t

nexts, transports, cusps_time, carries = [], [], [], []
row_at = list(row)

for position in range(1, PLANES):
    t = perf_counter()
    lift, element = next(splittings)
    nexts.append(perf_counter() - t)

    t = perf_counter()
    transported = lift.transport_isotropic_object(source)
    quotient.register_isotropic_lift(transported, lift, family, element)
    transports.append(perf_counter() - t)

    t = perf_counter()
    row_at.append(_arithmetic_cusp(subgroup, transported))
    cusps_time.append(perf_counter() - t)
    del transported

    t = perf_counter()
    _composite_divided_class_action(quotient, element, identity_element)
    carries.append(perf_counter() - t)

    # No collection inside the loop: a full gc on a heap of live category
    # objects costs hundreds of milliseconds at a few thousand planes and grows
    # with the row, which would be a timer of the probe's making and not the
    # row's cost.  RSS is read without it.
    if position < 3 or (position + 1) % max(1, PLANES // 10) == 0:
        print(f"  [plane {position + 1:7d}/{PLANES}] rss {rss_mib():8.1f} MiB", flush=True)
row = row_at
say(f"the row's first {len(row)} planes, shape cusps")


def band(values, count, label):
    if len(values) < 2 * count:
        count = max(1, len(values) // 2)
    head = values[:count]
    tail = values[-count:]
    print(
        f"  {label:22s} first {len(head):6d}: {1e3 * sum(head) / len(head):9.3f} ms a plane"
        f"   last {len(tail):6d}: {1e3 * sum(tail) / len(tail):9.3f} ms a plane"
        f"   all: {1e3 * sum(values) / len(values):9.3f} ms",
        flush=True,
    )


print("\n[per-plane stages]", flush=True)
band(nexts, BAND, "the split's walk")
band(transports, BAND, "transport and lift reg")
band(cusps_time, BAND, "the cusp (span key)")
band(carries, BAND, "the finite action")
totals = [a + b + c + d for a, b, c, d in zip(nexts, transports, cusps_time, carries, strict=True)]
band(totals, BAND, "the plane, all stages")
if source_cusp is not None:
    print(f"  the source plane's own cusp: {1e3 * source_cusp:.3f} ms", flush=True)

if INGRESS:
    points = tuple(row)
    print("\n[ingress: the library's own first statement, tuple(dict.fromkeys(...))]", flush=True)
    for count in PREFIXES:
        if count > len(points):
            continue
        t = perf_counter()
        distinct = tuple(dict.fromkeys(points[:count]))
        seconds = perf_counter() - t
        print(
            f"  {count:7d} points: {seconds:9.3f} s"
            f"   {1e6 * seconds / (count * (count - 1) / 2):8.1f} us a comparison"
            f"   {len(distinct)} distinct",
            flush=True,
        )
    if LIBRARY:
        t = perf_counter()
        admitted = finite_ordered_set(points[:LIBRARY])
        seconds = perf_counter() - t
        print(
            f"  finite_ordered_set over {LIBRARY} points: {seconds:9.3f} s"
            f"  (cardinality {int(admitted.cardinality().finite_value())})",
            flush=True,
        )
    if PAIRS:
        print("\n[one unequal pair of cusps, each timed]", flush=True)
        for offset in range(PAIRS):
            t = perf_counter()
            decision = points[offset] == points[offset + 1]
            print(
                f"  pair {offset:3d}/{PAIRS}: {1e3 * (perf_counter() - t):9.3f} ms"
                f"   equal={decision}",
                flush=True,
            )
    if PROFILE:
        import cProfile
        import pstats

        subject = points[:PROFILE]
        profiler = cProfile.Profile()
        t = perf_counter()
        profiler.enable()
        tuple(dict.fromkeys(subject))
        profiler.disable()
        print(
            f"\n[profile] dict.fromkeys over {len(subject)} cusps:"
            f" {perf_counter() - t:.3f} s",
            flush=True,
        )
        pstats.Stats(profiler).sort_stats("cumulative").print_stats(14)

gc.collect()
print(
    f"\n[RESULT] planes={len(row)} walk={walk:.1f} s rss_end={rss_mib():.1f} MiB"
    f" wall={perf_counter() - START:.1f} s lanes={{}}".replace("{}", ""),
    flush=True,
)
print(
    f"[BANDS] first={1e3 * sum(totals[:BAND]) / max(1, len(totals[:BAND])):.3f} ms"
    f" last={1e3 * sum(totals[-BAND:]) / max(1, len(totals[-BAND:])):.3f} ms a plane",
    flush=True,
)
