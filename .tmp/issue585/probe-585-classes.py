r"""Probe: what the incidence needs per plane, as class data, and what it costs.

At one plane ``P`` the incidence needs: the plane's registered lift, the one
covering of the row carried onto ``P``, and each covering line's divided class.
The certificate route builds the covering's carried lines as subobjects and
reads their classes from them.  The class route carries the classes themselves
by the finite image.  This probe checks the two agree, line by line and key by
key, and prices every step.
"""

import os
import sys
import threading
import time

START = time.monotonic()
PLANES = int(os.environ.get("PROBE_PLANES", "10"))


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


MARK = time.monotonic()


def stage(label):
    global MARK
    now = time.monotonic()
    print(f"    {now - MARK:9.2f} s  {label}  rss {rss_mib():8.1f} MiB", flush=True)
    MARK = now


from sage.libs.gap.libgap import libgap
from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.group.groups import _element_to_engine
from sage_extensions.categories.isotropic_orbits import (
    FlagType,
    _divided_discriminant_classes,
)
from sage_extensions.categories.orthogonal_quotients import (
    _isotropic_line_class_points,
    _isotropic_line_image_key,
    _plane_parabolic_incidence_flags,
)

SETWISE = libgap.function_factory(
    "function(x, g) return Set(List(x, y -> ImageElm(g, y))); end"
)

lattice = NamedLattices.Tco
names = {str(label): lattice.module_generator(label) for label in lattice.module_generating_set()}
first = lattice.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
plane = lattice.primitive_isotropic_subobject(first, names["ep"])
stage("T_Co and the row's plane")

subgroup = lattice.stable_orthogonal_group()
quotient = subgroup.finite_character_quotient()
stage("Otilde and its character quotient")
print(f"[probe] A_L = {lattice.discriminant_group()}", flush=True)
print(f"[probe] the plane's class set size: {len(_divided_discriminant_classes(lattice, plane))}", flush=True)

family = tuple(plane.parabolic_stabilizer_generators())
quotient.register_isotropic_lift(plane, quotient.supergroup.one(), family)
stage(f"the plane's parabolic: {len(family)} generators")

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
transport_witness = lifts[0]
transported_flag = transport_witness.transport_isotropic_object(ambient_flag)
covering = _plane_parabolic_incidence_flags(subgroup, planes[0], transported_flag)
print(f"[probe] the covering at the first plane: {len(covering)} flags", flush=True)
stage("the row's one covering, computed at the first plane")

reference_pairs = tuple(
    _isotropic_line_class_points(lattice, flag.terms()[0]) for flag in covering
)
print(f"[probe] the covering's class data: {[str(p) for p in reference_pairs]}", flush=True)
stage("the covering's class pairs")

# per-plane steps, priced separately
isometry_products = []
rho_direct = []
rho_via_image = []
engine_conversions = []
pair_carries = []
keys = []
span_lookups = []
plane_class_sets = []
moves = []
move_engines = []

for position in range(1, PLANES):
    plane_here = planes[position]
    move = lifts[position] * ~lifts[0]
    moves.append(move)

    mark = time.monotonic()
    record = quotient.isotropic_lift_of(plane_here)
    span_lookups.append(time.monotonic() - mark)
    assert record is not None
    move = record * ~lifts[0]

    mark = time.monotonic()
    rho_move = lattice.discriminant_representation()(move)
    rho_direct.append(time.monotonic() - mark)

    mark = time.monotonic()
    key_move = quotient.image(move)["discriminant"]
    rho_via_image.append(time.monotonic() - mark)

    mark = time.monotonic()
    engine_element = _element_to_engine(quotient._discriminant_group, rho_move)
    engine_conversions.append(time.monotonic() - mark)
    move_engines.append(engine_element)

    carried_here = []
    for pair in reference_pairs:
        mark = time.monotonic()
        carried = SETWISE(pair, engine_element)
        pair_carries.append(time.monotonic() - mark)
        carried_here.append(carried)

    mark = time.monotonic()
    plane_classes = _divided_discriminant_classes(lattice, plane_here)
    plane_class_sets.append(time.monotonic() - mark)

    if position <= 10:
        # the certificate route at the same plane, for comparison
        old_move = lifts[position] * ~lifts[0]
        carried_flags = tuple(old_move.transport_isotropic_object(flag) for flag in covering)
        for index, (flag, carried) in enumerate(zip(carried_flags, carried_here, strict=True)):
            line = flag.terms()[0]
            old_pair = _isotropic_line_class_points(lattice, line)
            agree_pair = str(old_pair) == str(carried)
            mark = time.monotonic()
            old_key = _isotropic_line_image_key(quotient, line)
            key_old = time.monotonic() - mark
            mark = time.monotonic()
            new_key = frozenset(quotient.isotropic_class_orbit(carried))
            key_new = time.monotonic() - mark
            print(
                f"  [plane {position} line {index}] class agrees: {agree_pair}"
                f"  key agrees: {old_key == new_key}"
                f"  old {1000 * key_old:8.3f} ms new {1000 * key_new:8.3f} ms"
                f"  key size {len(new_key)}",
                flush=True,
            )

print(
    f"[probe] RESULT planes={PLANES}"
    f" span_lookup_ms={1000 * sum(span_lookups) / len(span_lookups):.3f}"
    f" rho_direct_ms={1000 * sum(rho_direct) / len(rho_direct):.3f}"
    f" rho_via_image_ms={1000 * sum(rho_via_image) / len(rho_via_image):.3f}"
    f" engine_ms={1000 * sum(engine_conversions) / len(engine_conversions):.3f}"
    f" pair_carry_us={1e6 * sum(pair_carries) / len(pair_carries):.1f}"
    f" plane_classes_ms={1000 * sum(plane_class_sets) / len(plane_class_sets):.3f}"
    f" wall={time.monotonic() - START:.1f} s rss={rss_mib():.1f} MiB",
    flush=True,
)
