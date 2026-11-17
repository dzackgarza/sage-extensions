r"""Probe: the kernel plane row's per-plane cost, built as `cusps(2)` builds it.

One draw from the split iterator `_iter_splitting_isometries_in_im_rho(family)`,
one `transport_isotropic_object`, one `_span_key`, one `register_isotropic_lift`,
one cusp wrapper -- and, because `cusps` keeps cusps, no list of planes.  The
planes of the certificate route are also kept, so the two shapes can be priced
against each other on one process.

`PROBE_SHAPE=cusps` is the row `cusps(2)` builds after this issue's change
(spans only); `PROBE_SHAPE=representatives` is the row it builds before it (one
constructed plane per cusp, as `isotropic_orbit_representatives` returns them).
"""

import os
import time

START = time.monotonic()
PLANES = int(os.environ.get("PROBE_PLANES", "200"))
SHAPE = os.environ.get("PROBE_SHAPE", "representatives")


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


def stage(label):
    print(f"[{time.monotonic() - START:8.1f} s rss {rss_mib():8.1f} MiB] {label}", flush=True)


from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import _arithmetic_cusp, _span_key

lattice = NamedLattices.Tco
labels = tuple(lattice.module_generating_set())
names = {str(label): lattice.module_generator(label) for label in labels}
first_vector = lattice.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
plane = lattice.primitive_isotropic_subobject(first_vector, names["ep"])
subgroup = lattice.stable_orthogonal_group()
quotient = subgroup.finite_character_quotient()
stage(f"T_Co rank {lattice.module_rank()}, Otilde(T_Co), its character quotient")
family = tuple(plane.parabolic_stabilizer_generators())
stage(f"the plane's certified parabolic: {len(family)} generators")

splittings = quotient._iter_splitting_isometries_in_im_rho(family)
first_lift, first_element = next(splittings)
stage("the split's first lift (the finite image's whole coset walk)")

quotient.register_isotropic_lift(
    plane, quotient.supergroup.one(), family, quotient._discriminant_group.one()
)
row = []
times = []
samples = []
if SHAPE == "cusps":
    row.append(_arithmetic_cusp(subgroup, plane))
else:
    row.append(plane)
for position in range(1, PLANES):
    started = time.monotonic()
    lift, element = next(splittings)
    transported = lift.transport_isotropic_object(plane)
    quotient.register_isotropic_lift(transported, lift, family, element)
    if SHAPE == "cusps":
        row.append(_arithmetic_cusp(subgroup, transported))
        del transported
    else:
        row.append(transported)
    times.append(time.monotonic() - started)
    samples.append(rss_mib())
    if position < 3 or (position + 1) % max(1, PLANES // 8) == 0 or position + 1 == PLANES:
        print(f"  [plane {position + 1:6d}/{PLANES}] {times[-1] * 1000:8.1f} ms  rss {samples[-1]:8.1f} MiB",
              flush=True)
stage(f"the row's first {len(row)} entries, shape {SHAPE}")

band = max(1, (PLANES - 1) // 8)
print("\n[slope] per band of planes", flush=True)
for end in range(band, len(times) + 1, band):
    steps = band
    wall = sum(times[end - steps:end]) / steps
    print(
        f"  planes {end - steps + 2:6d}..{end + 1:6d}:"
        f" {wall * 1000:8.2f} ms a plane,"
        f" {1000 * (samples[end - 1] - samples[end - 1 - steps]) / steps:8.1f} KB a plane",
        flush=True,
    )
overall = 1024 * 1024 * (samples[-1] - samples[0]) / max(1, len(times))
mean_wall = sum(times) / len(times)
print(
    f"\n[RESULT] shape={SHAPE} planes={len(row)} wall={time.monotonic() - START:.1f} s"
    f" mean_per_plane_ms={mean_wall * 1000:.2f}"
    f" rss_start={samples[0]:.1f} MiB rss_end={samples[-1]:.1f} MiB"
    f" growth_per_plane_bytes={overall:.0f}"
    f" lifts_retained={len(quotient.__dict__.get('_isotropic_lift_registry', {}))}"
    f" at_189720_planes_s={mean_wall * 189720:.0f}"
    f" at_189720_planes_GiB={overall * 189720 / 1024 ** 3:.2f}",
    flush=True,
)
