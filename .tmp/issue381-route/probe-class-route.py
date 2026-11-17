r"""Probe: the divided-class route's per-plane work on the same Otilde plane row.

`tits_building_incidence_by_divided_classes` walks the plane cusps and, at each
one, reads the registered lift's finite element, composes
`target * ~reference` in `O(A_L)`, carries the covering's three class pairs by
it, and names each carried pair's line cusp by the row's index.  This probe
runs exactly those steps on PROBE_PLANES planes of the row and records the cost
of each, so the two routes can be compared on one tree and one row.

The cusp rows are not built here: the line index costs the 527-cusp line row
(> 552 s on this tree, `.tmp/issue585/linerow.log`), and this probe measures the
walk's own per-plane terms, not the rows.
"""
import os
import time

START = time.monotonic()
PLANES = int(os.environ.get("PROBE_PLANES", "200"))


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import _span_key
from sage_extensions.categories.orthogonal_quotients import (
    _carried_divided_classes,
    _composite_divided_class_action,
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
family = tuple(plane.parabolic_stabilizer_generators())
splittings = quotient._iter_splitting_isometries_in_im_rho(family)
lift0, element0 = next(splittings)
planes = [lift0.transport_isotropic_object(plane)]
quotient.register_isotropic_lift(planes[0], lift0, family, element0)
print(f"[{time.monotonic() - START:8.1f} s rss {rss_mib():8.1f} MiB] the split's first lift", flush=True)

for position in range(1, PLANES):
    lift, element = next(splittings)
    planes.append(lift.transport_isotropic_object(plane))
    quotient.register_isotropic_lift(planes[-1], lift, family, element)
print(f"[{time.monotonic() - START:8.1f} s rss {rss_mib():8.1f} MiB] {len(planes)} planes registered", flush=True)

ambient_flag = lattice.isotropic_flag(first, names["ep"])
covering = _plane_parabolic_incidence_flags(subgroup, planes[0], lift0.transport_isotropic_object(ambient_flag))
print(f"[{time.monotonic() - START:8.1f} s rss {rss_mib():8.1f} MiB] the covering: "
      f"{None if covering is None else len(covering)} flags", flush=True)
pairs = tuple(_isotropic_line_class_points(lattice, flag.terms()[0]) for flag in covering)

steps = []
samples = []
reference_lift, reference_image = quotient.registered_isotropic_lift(planes[0])
for position in range(1, PLANES):
    started = time.monotonic()
    target_lift, target_image = quotient.registered_isotropic_lift(planes[position])
    move = target_lift * ~reference_lift
    action = _composite_divided_class_action(quotient, target_image, reference_image)
    for pair in pairs:
        carried = _carried_divided_classes(pair, action)
        frozenset(quotient.isotropic_class_orbit(carried))
    steps.append(time.monotonic() - started)
    samples.append(rss_mib())
print(f"[{time.monotonic() - START:8.1f} s rss {rss_mib():8.1f} MiB] the walk over {len(steps)} planes", flush=True)

band = max(1, len(steps) // 8)
for end in range(band, len(steps) + 1, band):
    print(f"  planes {end - band + 1:6d}..{end:6d}: {1000 * sum(steps[end - band:end]) / band:8.2f} ms a plane,"
          f" {1000 * (samples[end - 1] - samples[end - 1 - band]) / band:8.1f} KB a plane", flush=True)
mean = sum(steps) / len(steps)
growth = 1024 * 1024 * (samples[-1] - samples[0]) / max(1, len(samples) - 1)
print(f"\n[RESULT] planes={len(steps)} mean_per_plane_ms={mean * 1000:.3f}"
      f" growth_per_plane_bytes={growth:.0f}"
      f" at_189720_planes_s={mean * 189720:.0f}"
      f" at_189720_planes_GiB={growth * 189720 / 1024 ** 3:.2f}"
      f" wall={time.monotonic() - START:.1f} s rss={rss_mib():.1f} MiB", flush=True)
