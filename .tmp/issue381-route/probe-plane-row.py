r"""Probe: the kernel plane row's and the certificate walk's per-plane cost on T_Co.

Phase A -- the plane row (`cusps(2)`), built exactly as
`_plane_orbit_from_parabolic_stabilizer` builds it: one draw from the split
iterator `_iter_splitting_isometries_in_im_rho(family)` (which yields
`(lift, finite element)`), one `transport_isotropic_object(plane)`, one
`_span_key`, one `register_isotropic_lift(transported, lift, family, element)`,
and the cusp wrapper `_arithmetic_cusp(subgroup, transported)` the cusp row
keeps.  Per-plane wall time and VmRSS after every plane.

Phase B -- the certificate walk's per-plane subobject work: the row's covering
is computed once at the first plane by `_plane_parabolic_incidence_flags` and
carried to each further plane by `transport_covering`, whose carried flags the
plane's certificates retain.  The flag the covering is computed over is built
from the slicing plane's own basis (`lattice.isotropic_flag`) in place of the
ambient flag row, which is a fixed cost of the call and not a per-plane one --
a stated departure from the call, as in results/issue381-kernel-row-runner-kill.md.
"""
import os
import sys
import time

START = time.monotonic()
PLANES = int(os.environ.get("PROBE_PLANES", "200"))
WALK = int(os.environ.get("PROBE_WALK", "40"))


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
from sage_extensions.categories.orthogonal_quotients import (
    _plane_parabolic_incidence_flags,
)

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
print(f"[probe] the slicing plane is parabolic complete: {plane.is_parabolic_complete()}", flush=True)
family = tuple(plane.parabolic_stabilizer_generators())
stage(f"the plane's certified parabolic: {len(family)} generators")

splittings = quotient._iter_splitting_isometries_in_im_rho(family)
first_lift, first_element = next(splittings)
stage("the split's first lift (the finite image's whole coset walk)")
print(f"[probe] the split yields (lift, element): {type(first_lift).__name__}, "
      f"{type(first_element).__name__}", flush=True)

# ---- Phase A: the plane row -------------------------------------------------
planes = []
cusps = []
times = []
samples = []
two = first_lift
for position in range(PLANES):
    started = time.monotonic()
    if position == 0:
        lift, element = first_lift, first_element
    else:
        lift, element = next(splittings)
    transported = lift.transport_isotropic_object(plane)
    span = _span_key(transported)
    quotient.register_isotropic_lift(transported, lift, family, element)
    cusp = _arithmetic_cusp(subgroup, transported)
    planes.append(transported)
    cusps.append(cusp)
    times.append(time.monotonic() - started)
    samples.append(rss_mib())
    if position < 3 or (position + 1) % max(1, PLANES // 8) == 0 or position + 1 == PLANES:
        print(f"  [plane {position + 1:6d}/{PLANES}] {times[-1] * 1000:8.1f} ms  rss {samples[-1]:8.1f} MiB",
              flush=True)
stage(f"the plane row's first {len(planes)} planes")

band = max(1, PLANES // 8)
print("\n[slope] the plane row, per band of planes", flush=True)
for end in range(band, PLANES + 1, band):
    steps = band
    wall = sum(times[end - steps:end]) / steps
    print(
        f"  planes {end - steps + 1:6d}..{end:6d}:"
        f" {wall * 1000:8.2f} ms a plane,"
        f" {1000 * (samples[end - 1] - samples[end - 1 - steps]) / steps:8.1f} KB a plane",
        flush=True,
    )
overall = 1024 * 1024 * (samples[-1] - samples[0]) / max(1, len(planes) - 1)
mean_wall = sum(times) / len(times)
print(
    f"\n[RESULT-A] planes={len(planes)} wall={time.monotonic() - START:.1f} s"
    f" mean_per_plane_ms={mean_wall * 1000:.2f}"
    f" tail_per_plane_ms={sum(times[-band:]) / band * 1000:.2f}"
    f" rss_start={samples[0]:.1f} MiB rss_end={samples[-1]:.1f} MiB"
    f" growth_per_plane_bytes={overall:.0f}"
    f" lifts_retained={len(quotient.__dict__.get('_isotropic_lift_registry', {}))}"
    f" at_189720_planes_s={mean_wall * 189720:.0f}"
    f" at_189720_planes_GiB={overall * 189720 / 1024 ** 3:.2f}",
    flush=True,
)

# ---- Phase B: the certificate walk's per-plane subobject work ---------------
base = time.monotonic()
flag0 = lattice.isotropic_flag(first_vector, names["ep"])
stage("a flag over the slicing plane, from its own basis")
covering = _plane_parabolic_incidence_flags(subgroup, planes[0], flag0)
stage(f"the covering at the first plane: {None if covering is None else len(covering)} flags")
if covering is None:
    print("[probe] no parabolic covering at the first plane; phase B not run", flush=True)
    sys.exit(0)
quotient.register_isotropic_covering(planes[0], 0, quotient.isotropic_lift_of(planes[0]), covering)
reference_plane, reference_lift, reference_flags = quotient.isotropic_covering_reference(0)

walk_times = []
walk_samples = []
kept = []
for position in range(1, WALK + 1):
    started = time.monotonic()
    target_lift = quotient.isotropic_lift_of(planes[position])
    carried = quotient.transport_covering(reference_lift, reference_flags, target_lift)
    kept.append(carried)
    walk_times.append(time.monotonic() - started)
    walk_samples.append(rss_mib())
    if position < 3 or position % max(1, WALK // 8) == 0 or position == WALK:
        print(f"  [carry {position:6d}/{WALK}] {walk_times[-1] * 1000:8.1f} ms  rss {walk_samples[-1]:8.1f} MiB",
              flush=True)
stage(f"the covering carried to {WALK} planes")

band = max(1, WALK // 8)
print("\n[slope] the certificate walk's carry, per band of planes", flush=True)
for end in range(band, WALK + 1, band):
    steps = band
    print(
        f"  planes {end - steps + 1:6d}..{end:6d}:"
        f" {sum(walk_times[end - steps:end]) / steps * 1000:8.2f} ms a plane,"
        f" {1000 * (walk_samples[end - 1] - walk_samples[end - 1 - steps]) / steps:8.1f} KB a plane",
        flush=True,
    )
walk_overall = 1024 * 1024 * (walk_samples[-1] - walk_samples[0]) / max(1, len(walk_samples) - 1)
walk_wall = sum(walk_times) / len(walk_times)
print(
    f"\n[RESULT-B] planes={len(kept)} mean_per_plane_ms={walk_wall * 1000:.2f}"
    f" growth_per_plane_bytes={walk_overall:.0f}"
    f" carried_flags_a_plane={len(kept[0])}"
    f" at_189720_planes_s={walk_wall * 189720:.0f}"
    f" at_189720_planes_GiB={walk_overall * 189720 / 1024 ** 3:.2f}"
    f" total_wall={time.monotonic() - START:.1f} s rss={rss_mib():.1f} MiB",
    flush=True,
)
