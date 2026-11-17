r"""Probe: the plane row's per-plane cost at 10, 100 and 200 planes, and what it retains.

One draw from the split iterator `_iter_splitting_isometries_in_im_rho(family)`,
one `transport_isotropic_object`, one `_span_key`, one `register_isotropic_lift`,
one cusp wrapper.  `PROBE_SHAPE=representatives` keeps the constructed plane of
each draw (the row before the pilot); `PROBE_SHAPE=cusps` keeps the cusp named by
the plane's span and drops the plane (the row after it).

The last line counts the live objects of the plane's own class beside the one
source plane the draws start from, so the row's answer to "does it retain a
representative" is a number and not an inference.
"""

import gc
import os
import time

START = time.monotonic()
PLANES = int(os.environ.get("PROBE_PLANES", "200"))
SHAPE = os.environ.get("PROBE_SHAPE", "representatives")
CHECKPOINTS = tuple(
    int(entry) for entry in os.environ.get("PROBE_CHECKPOINTS", "10,100,200").split(",")
)


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


def stage(label):
    print(f"[{time.monotonic() - START:8.1f} s rss {rss_mib():8.1f} MiB] {label}", flush=True)


from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import _arithmetic_cusp

lattice = NamedLattices.Tco
labels = tuple(lattice.module_generating_set())
names = {str(label): lattice.module_generator(label) for label in labels}
first_vector = lattice.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
source = lattice.primitive_isotropic_subobject(first_vector, names["ep"])
plane_class = type(source)
subgroup = lattice.stable_orthogonal_group()
quotient = subgroup.finite_character_quotient()
stage(f"T_Co rank {lattice.module_rank()}, Otilde(T_Co), its character quotient")
family = tuple(source.parabolic_stabilizer_generators())
stage(f"the plane's certified parabolic: {len(family)} generators")

splittings = quotient._iter_splitting_isometries_in_im_rho(family)
first_lift, first_element = next(splittings)
stage("the split's first lift (the finite image's whole coset walk)")

quotient.register_isotropic_lift(
    source, quotient.supergroup.one(), family, quotient._discriminant_group.one()
)
row = []
marks = []
row.append(source if SHAPE == "representatives" else _arithmetic_cusp(subgroup, source))
gc.collect()
marks.append((1, rss_mib()))
for position in range(1, PLANES):
    lift, element = next(splittings)
    transported = lift.transport_isotropic_object(source)
    quotient.register_isotropic_lift(transported, lift, family, element)
    row.append(
        transported if SHAPE == "representatives" else _arithmetic_cusp(subgroup, transported)
    )
    del transported
    if position % 25 == 0:
        gc.collect()
    if position + 1 in CHECKPOINTS:
        marks.append((position + 1, rss_mib()))
    if position < 3 or (position + 1) % max(1, PLANES // 8) == 0 or position + 1 == PLANES:
        print(f"  [plane {position + 1:6d}/{PLANES}] rss {rss_mib():8.1f} MiB", flush=True)
stage(f"the row's first {len(row)} entries, shape {SHAPE}")

gc.collect()
planes_alive = sum(
    1
    for candidate in gc.get_objects()
    if type(candidate) is plane_class and candidate is not source
)
print("\n[slope] over the checkpoints", flush=True)
for (start_at, start_rss), (end_at, end_rss) in zip(marks, marks[1:]):
    steps = end_at - start_at
    print(
        f"  planes {start_at:6d}..{end_at:6d}:"
        f" {(end_rss - start_rss) * 1024 / steps:9.1f} KiB a plane",
        flush=True,
    )
print(
    f"\n[RESULT] shape={SHAPE} planes={len(row)} wall={time.monotonic() - START:.1f} s"
    f" rss_end={marks[-1][1]:.1f} MiB"
    f" planes_alive_beside_the_source={planes_alive}"
    f" lifts_retained={len(quotient.__dict__.get('_isotropic_lift_registry', {}))}",
    flush=True,
)
