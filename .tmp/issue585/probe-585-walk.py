r"""Probe: the class route's walk over the T_Co planes, its per-plane RSS and wall.

The row is the same one the carry probe of ``results/issue585-the-walks-per-plane-retainer.md``
walks: ``Otilde(T_Co) = ker rho``, its parabolic split's lifts and the planes they
transport the base plane to.  The walk here is the class route's per-plane work --
the registered lift's span lookup, the finite image's action on ``A_L``, the
three carried class pairs and their keys -- and nothing else: no flag, no
subobject and no transport of a carried line.

``PROBE_PHASE=check`` runs the certificate route's own per-plane work beside it
(the carry, the three line keys, the release) and compares, at every line of
every plane, the carried class pair with the class pair of the carried line and
the two keys with each other.  That is the equality of the deciding data; the
edge sets themselves are compared on the lattices whose line row returns.
"""

import os
import sys
import threading
import time

START = time.monotonic()
PLANES = int(os.environ.get("PROBE_PLANES", "1000"))
PHASE = os.environ.get("PROBE_PHASE", "row")
CHECK = PHASE.endswith("check")
TRACE = "trace" in PHASE


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


MARK = time.monotonic()
BANDS = []


def stage(label):
    global MARK
    now = time.monotonic()
    print(f"    {now - MARK:9.2f} s  {label}  rss {rss_mib():8.1f} MiB", flush=True)
    MARK = now


from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import FlagType
from sage_extensions.categories.orthogonal_quotients import (
    _carried_divided_classes,
    _divided_class_action,
    _isotropic_line_class_points,
    _isotropic_line_image_key,
    _plane_parabolic_incidence_flags,
)

lattice = NamedLattices.Tco
names = {str(label): lattice.module_generator(label) for label in lattice.module_generating_set()}
first = lattice.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
plane = lattice.primitive_isotropic_subobject(first, names["ep"])
subgroup = lattice.stable_orthogonal_group()
quotient = subgroup.finite_character_quotient()
stage("T_Co, Otilde and its character quotient")

family = tuple(plane.parabolic_stabilizer_generators())
quotient.register_isotropic_lift(plane, quotient.supergroup.one(), family)
stage(f"the plane's parabolic: {len(family)} generators")

SOURCE = "products" if PHASE.startswith("products") else "row"
if SOURCE == "products":
    # The row's split is one-off work of minutes under this VM's load, and the
    # per-plane work does not read the row: it reads the plane's span, the
    # lift's discriminant image and the three class pairs.  This mode takes the
    # planes as the images of the base plane under powers of one ambient
    # generator, so the per-plane cost and its retention are measured on the
    # same operations without paying the split.
    generators = tuple(lattice.Aut().group_generators())
    lifts = [quotient.supergroup.one()]
    planes = [plane]
    for position in range(1, PLANES):
        first = generators[position % len(generators)]
        second = generators[(position // len(generators)) % len(generators)]
        current = first * second
        lifts.append(current)
        planes.append(current.transport_isotropic_object(plane))
        quotient.register_isotropic_lift(planes[-1], current, family)
    stage(
        f"{len(planes)} planes, one registered lift each"
        f" (products of two of the {len(generators)} ambient generators)"
    )
else:
    splittings = quotient._iter_splitting_isometries_in_im_rho(family)
    first_splitting = next(splittings)
    stage("the split's first lift")
    lifts = [first_splitting]
    planes = [first_splitting.transport_isotropic_object(plane)]
    quotient.register_isotropic_lift(planes[0], first_splitting, family)
    for position in range(1, PLANES):
        splitting = next(splittings)
        lifts.append(splitting)
        planes.append(splitting.transport_isotropic_object(plane))
        quotient.register_isotropic_lift(planes[-1], splitting, family)
    stage(f"{len(planes)} planes of the row, one registered lift each")

basis = tuple(plane.inclusion().domain().module_generating_set())
vectors = tuple(plane.inclusion()(plane.inclusion().domain().module_generator(label)) for label in basis)
ambient_flag = lattice.isotropic_flag(vectors[0], vectors[1], flag_type=FlagType((1, 2)))
transported_flag = lifts[0].transport_isotropic_object(ambient_flag)
covering = _plane_parabolic_incidence_flags(subgroup, planes[0], transported_flag)
reference_pairs = tuple(
    _isotropic_line_class_points(lattice, flag.terms()[0]) for flag in covering
)
stage(f"the row's one covering ({len(covering)} flags) and its class pairs")

if TRACE:
    import tracemalloc

    tracemalloc.start(20)
snapshots = {}

index = {}
edges = []
walk = []
phases = {"product": [], "span": [], "morphism": [], "carry": [], "keys": []}
old_walk = []
comparisons = 0
agreements = 0
key_seen = {}
band = max(1, PLANES // 10)
mark = time.monotonic()
for position in range(1, PLANES):
    step = time.monotonic()
    lift = quotient.isotropic_lift_of(planes[position])
    if lift is None:
        raise AssertionError(f"plane {position} has no registered lift")
    spanned = time.monotonic()
    move = lift * ~lifts[0]
    produced = time.monotonic()
    action = _divided_class_action(quotient, move)
    acted = time.monotonic()
    carried_here = []
    for classes in reference_pairs:
        carried_here.append(_carried_divided_classes(classes, action))
    carried_done = time.monotonic()
    for carried in carried_here:
        key = frozenset(quotient.isotropic_class_orbit(carried))
        slot = index.setdefault(key, len(index))
        edges.append((slot, position))
    keyed = time.monotonic()
    walk.append(keyed - step)
    phases["span"].append(spanned - step)
    phases["product"].append(produced - spanned)
    phases["morphism"].append(acted - produced)
    phases["carry"].append(carried_done - acted)
    phases["keys"].append(keyed - carried_done)
    if CHECK and position < 100:
        start = time.monotonic()
        old_move = lifts[position] * ~lifts[0]
        old_flags = tuple(old_move.transport_isotropic_object(flag) for flag in covering)
        old_lines = [flag.terms()[0] for flag in old_flags]
        for line, carried in zip(old_lines, carried_here, strict=True):
            old_key = _isotropic_line_image_key(quotient, line)
            comparisons += 1
            agree_class = str(_isotropic_line_class_points(lattice, line)) == str(carried)
            agree_key = old_key == frozenset(quotient.isotropic_class_orbit(carried))
            if agree_class and agree_key:
                agreements += 1
            else:
                print(f"  [DISAGREE plane {position}] class {agree_class} key {agree_key}", flush=True)
        quotient.release_isotropic_transports(old_lines)
        old_walk.append(time.monotonic() - start)
    if position < 10 or (position + 1) % band == 0 or position + 1 == PLANES:
        now = time.monotonic()
        BANDS.append((position + 1, rss_mib(), 1000 * sum(walk[-band:]) / min(band, len(walk[-band:]))))
        if TRACE and position + 1 in (100, PLANES):
            snapshots[position + 1] = tracemalloc.take_snapshot()
            if len(snapshots) == 2:
                first, second = snapshots[100], snapshots[PLANES]
                growth = second.compare_to(first, "traceback")
                print(f"[trace] the {PLANES - 100} planes between 100 and {PLANES}:", flush=True)
                for statistic in growth[:6]:
                    frames = statistic.traceback.format()[-4:]
                    print(
                        f"[trace]   {statistic.size_diff / 1024:.1f} KiB"
                        f" in {statistic.count_diff} blocks"
                        f"  {' | '.join(frame.strip() for frame in frames)}",
                        flush=True,
                    )
        print(
            f"  [walk plane {position + 1:6d}/{PLANES}] {now - mark:9.3f} s"
            f"  {1000 * sum(walk[-band:]) / min(band, len(walk[-band:])):7.3f} ms a plane"
            f"  rss {rss_mib():8.1f} MiB  keys {len(index)}  edges {len(edges)}"
            f"  [{' '.join(f'{name} {1000 * sum(values[-band:]) / min(band, len(values[-band:])):.2f}' for name, values in phases.items())} ms]"
            + (f"  old {1000 * sum(old_walk[-band:]) / max(1, len(old_walk[-band:])):7.3f} ms" if CHECK else ""),
            flush=True,
        )
        mark = now
stage(f"the walk over {len(walk)} planes")
print(
    f"[probe] RESULT phase={'check' if CHECK else 'row'} planes={PLANES}"
    f" walk_ms={1000 * sum(walk) / len(walk):.4f}"
    f" keys={len(index)} edges={len(edges)}"
    f" comparisons={comparisons} agreements={agreements}"
    f" old_ms={1000 * sum(old_walk) / max(1, len(old_walk)):.3f}"
    f" bands={[(size, round(mib, 1)) for size, mib, _ in BANDS]}"
    f" wall={time.monotonic() - START:.1f} s rss={rss_mib():.1f} MiB",
    flush=True,
)
