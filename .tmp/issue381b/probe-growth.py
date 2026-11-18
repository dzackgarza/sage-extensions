"""What one plane of a kernel incidence row costs, and which term grows with the planes before it.

The row is drawn exactly as the driver draws it -- ``_yield_subgroup_isotropic_orbit_representatives``
through ``_arithmetic_cusp``, so the plane is built by the split's own transport and the cusp is
the span -- and then the relation's per-plane body is replayed one plane at a time with each step
timed separately, in bands, so a term that grows with the plane's position is separated from one
that is constant.  Nothing here is the relation: it is the relation's own calls, in its own order.
"""

import os
import resource
import sys
import time

sys.path.insert(0, "/repos/sage-extensions/tests")

from sage_extensions.all import *  # noqa: F401,F403
import sage_extensions.categories.isotropic_orbits as isotropic_orbits  # noqa: E402
import sage_extensions.categories.orthogonal_quotients as orthogonal_quotients  # noqa: E402

from coble_gamma_co_2_incidence_rows import (  # noqa: E402
    _lattice_by_name,
    _row_subgroup,
)

ROW = os.environ.get("PROBE_ROW", "Otilde")
PLANES = int(os.environ.get("PROBE_PLANES", "300"))
BAND = int(os.environ.get("PROBE_BAND", "25"))
start = time.monotonic()
clock = lambda: time.monotonic() - start  # noqa: E731


def rss_mib():
    return int(open("/proc/self/status").read().split("VmRSS:")[1].split()[0]) / 1024


def mark(what):
    print(f"[{clock():9.1f} s rss {rss_mib():8.1f} MiB] {what}", flush=True)


lattice = _lattice_by_name("Tco")
subgroup = _row_subgroup(lattice, ROW)
quotient = subgroup.finite_character_quotient()
mark(f"T_Co and the {ROW} row's subgroup")

ambient_planes = tuple(lattice.Aut().isotropic_orbit_representatives(2))
complete = tuple(plane.is_parabolic_complete() for plane in ambient_planes)
mark(f"the ambient plane row: {len(ambient_planes)} plane(s), parabolic complete {complete}")
if not all(decision is True for decision in complete):
    raise SystemExit("this process's ambient plane representative is not certified complete")

# A class set of the shape the relation carries: the divided class pair of an isotropic
# line, read off the ambient plane's own basis so that no line row has to be built.
plane0 = ambient_planes[0]
inclusion0 = plane0.inclusion()
label0 = next(iter(inclusion0.domain().module_generating_set()))
line = lattice.primitive_isotropic_subobject(
    inclusion0(inclusion0.domain().module_generator(label0))
)
classes = orthogonal_quotients._isotropic_line_class_points(lattice, line)
mark("a carried class set, from a line of the ambient plane")
del plane0, inclusion0, label0, line

spans = []
drawn = []


def draw():
    from sage_extensions.categories.isotropic_orbits import _arithmetic_cusp
    from sage_extensions.categories.orthogonal_quotients import (
        _yield_subgroup_isotropic_orbit_representatives,
    )

    walk_started = time.monotonic()
    for position, plane in enumerate(
        _yield_subgroup_isotropic_orbit_representatives(subgroup, 2)
    ):
        if position:
            drawn.append((position, time.monotonic() - previous, rss_mib()))
        previous = time.monotonic()
        cusp = _arithmetic_cusp(subgroup, plane)
        spans.append(cusp.span())
        if position + 1 >= PLANES:
            mark(f"the walk: {PLANES} planes drawn in {time.monotonic() - walk_started:.1f} s")
            break
    del plane


draw()
mark(f"drawn: {len(drawn)} transport intervals recorded, rss after the planes are dropped")

# The reference lift of the covering: position 0's registered lift and its finite element.
reference_plane = isotropic_orbits._subobject_of_span(lattice, spans[0])
reference_lift, reference_image = quotient.registered_isotropic_lift(reference_plane)
mark("the reference plane's lift")
del reference_plane

STEPS = (
    "rebuild",
    "span key",
    "registry",
    "inverse reference",
    "integral move",
    "finite action",
    "carried classes",
    "class orbit",
)
samples = {name: [] for name in STEPS}


def timed(name, call):
    opened = time.monotonic()
    answer = call()
    samples[name].append(time.monotonic() - opened)
    return answer


for position, span in enumerate(spans):
    plane = timed("rebuild", lambda: isotropic_orbits._subobject_of_span(lattice, span))
    timed("span key", lambda: isotropic_orbits._span_key(plane))
    registered = timed(
        "registry", lambda: quotient.registered_isotropic_lift(plane)
    )
    target_lift, target_image = registered
    inverted = timed("inverse reference", lambda: ~reference_lift)
    timed("integral move", lambda: target_lift * inverted)
    action = timed(
        "finite action",
        lambda: orthogonal_quotients._composite_divided_class_action(
            quotient, target_image, reference_image
        ),
    )
    carried = timed(
        "carried classes",
        lambda: orthogonal_quotients._carried_divided_classes(classes, action),
    )
    timed("class orbit", lambda: quotient.isotropic_class_orbit(carried))
    del plane
    if (position + 1) % 50 == 0:
        mark(f"the replay: {position + 1} planes, rss {rss_mib():.1f} MiB")


def bands(name):
    values = samples[name]
    if not values:
        return ""
    cut = max(1, min(BAND, len(values) // 3))
    head = sum(values[:cut]) / cut
    middle = sum(values[cut:-cut] or values) / len(values[cut:-cut] or values)
    tail = sum(values[-cut:]) / cut
    return f"  {name:18s} {1000 * head:8.3f} {1000 * middle:8.3f} {1000 * tail:8.3f}  (ms a plane)"


print()
print(f"the relation's per-plane body, replayed on {len(spans)} drawn planes of {ROW}(T_Co)")
print(f"  {'step':18s} {'first':>8s} {'middle':>8s} {'last':>8s}")
for name in STEPS:
    print(bands(name))
total = {name: sum(samples[name]) for name in STEPS}
print(f"  {'sum':18s} {1000 * sum(total.values()) / len(spans):8.3f}")
print()
print("the split's own per-plane interval, drawn planes 1..N:")
if drawn:
    cut = max(1, min(BAND, len(drawn) // 3))
    intervals = [interval for _, interval, _ in drawn]
    print(
        f"  {'transport + cusp':18s} {1000 * sum(intervals[:cut]) / cut:8.3f} "
        f"{1000 * sum(intervals[cut:-cut]) / len(intervals[cut:-cut]):8.3f} "
        f"{1000 * sum(intervals[-cut:]) / cut:8.3f}  (ms a plane)"
    )
    print(f"  resident after the last plane: {drawn[-1][2]:.1f} MiB")
print(f"[{clock():9.1f} s rss {rss_mib():8.1f} MiB] done")
