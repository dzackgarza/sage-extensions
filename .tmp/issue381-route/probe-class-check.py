r"""Probe: every carried class pair of the divided-class route against the carried line.

The class route's own check is made once per source family: at the first plane
that is not the covering's own, the class pair the finite image carries is
compared with the class pair of the line the lattice actually carries there.
This probe makes that comparison at every plane of a slice, so the route's
per-plane agreement is a count and not a single row.

``_carried_divided_classes(pair, action)`` is the carried datum;
``_isotropic_line_class_points(lattice, move.transport_isotropic_object(flag).terms()[0])``
is the datum of the carried line, which is what the route's check compares.
"""
import os
import time

START = time.monotonic()
PLANES = int(os.environ.get("PROBE_PLANES", "120"))


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.orthogonal_quotients import (
    _carried_divided_classes,
    _composite_divided_class_action,
    _isotropic_line_class_points,
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
print(f"[{time.monotonic() - START:8.1f} s] the split's first lift", flush=True)
for _ in range(1, PLANES):
    lift, element = next(splittings)
    planes.append(lift.transport_isotropic_object(plane))
    quotient.register_isotropic_lift(planes[-1], lift, family, element)
print(f"[{time.monotonic() - START:8.1f} s] {len(planes)} planes registered", flush=True)

ambient_flag = lattice.isotropic_flag(first, names["ep"])
covering = _plane_parabolic_incidence_flags(subgroup, planes[0], lift0.transport_isotropic_object(ambient_flag))
print(f"[{time.monotonic() - START:8.1f} s] the covering: {len(covering)} flags", flush=True)
pairs = tuple(_isotropic_line_class_points(lattice, flag.terms()[0]) for flag in covering)
reference_lift, reference_image = quotient.registered_isotropic_lift(planes[0])

agreements = 0
comparisons = 0
for position in range(1, PLANES):
    target_lift, target_image = quotient.registered_isotropic_lift(planes[position])
    move = target_lift * ~reference_lift
    action = _composite_divided_class_action(quotient, target_image, reference_image)
    for flag, pair in zip(covering, pairs, strict=True):
        carried = _carried_divided_classes(pair, action)
        image_line = move.transport_isotropic_object(flag).terms()[0]
        comparisons += 1
        if str(_isotropic_line_class_points(lattice, image_line)) == str(carried):
            agreements += 1
        else:
            print(f"  [disagreement at plane {position}, flag {flag}]", flush=True)
print(
    f"[RESULT] planes={PLANES - 1} comparisons={comparisons} agreements={agreements}"
    f" wall={time.monotonic() - START:.1f} s rss={rss_mib():.1f} MiB",
    flush=True,
)
