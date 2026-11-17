r"""Probe: the incidence walk's per-plane work on T_Co, measured directly.

``PredicateSubgroups.tits_building_incidence`` walks the plane cusps of the row
and, at each plane, carries the row's one covering there
(``OrthogonalCharacterQuotient.transport_covering``), reads each carried line's
key in the finite image (``_isotropic_line_image_key``) and makes the plane's
certificates.  The public call recomputes the 527-cusp line row before it walks,
and on this tree that row alone has not returned inside a ten-minute command
(the stack-sampled diagnostic ``diag-1.log`` was still inside
``_isotropic_line_class_points`` at 559.5 s), so the call cannot be reached
inside one command from here.

What this probe measures instead is the walk's own per-plane work on the row's
own objects: one covering computed at the first plane by the function the walk
calls (``_plane_parabolic_incidence_flags``), then the carry to each further
plane with the same registered lifts, the same ``transport_covering`` call and
the same release of the carried lines' transports, plus the three line keys the
walk reads at each plane.  It is a reconstruction of the walk's per plane cost
and not the call, and no count of certificates comes out of it.
"""

import os
import sys
import threading
import time

START = time.monotonic()
PLANES = int(os.environ.get("PROBE_PLANES", "10"))
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
        print(f"[rss] t={time.monotonic() - START:7.1f}s rss={rss_mib():8.1f} MiB", flush=True)


threading.Thread(target=sample, daemon=True).start()

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import FlagType
from sage_extensions.categories.orthogonal_quotients import (
    _isotropic_line_image_key,
    _plane_parabolic_incidence_flags,
)

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


lattice = NamedLattices.Tco
names = {str(label): lattice.module_generator(label) for label in lattice.module_generating_set()}
first = lattice.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
plane = lattice.primitive_isotropic_subobject(first, names["ep"])
print(f"[probe] the walk's per-plane work over {PLANES} planes of the row", flush=True)
stage("T_Co and the row's plane")

subgroup = lattice.stable_orthogonal_group()
quotient = subgroup.finite_character_quotient()
stage("Otilde and its character quotient")

print(f"[probe] the plane is parabolic complete: {plane.is_parabolic_complete()}", flush=True)
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
transported_flag = first_splitting.transport_isotropic_object(ambient_flag)
covering = _plane_parabolic_incidence_flags(subgroup, planes[0], transported_flag)
print(f"[probe] the covering at the first plane: {covering if covering is None else len(covering)} flags", flush=True)
stage("the row's one covering, computed at the first plane")

carries = []
keys = []
releases = []
band = max(1, PLANES // 10)
mark = time.monotonic()
for position in range(1, PLANES):
    carry_start = time.monotonic()
    carried = quotient.transport_covering(lifts[0], covering, lifts[position])
    carry_done = time.monotonic()
    lines = [flag.terms()[0] for flag in carried]
    for line in lines:
        _isotropic_line_image_key(quotient, line)
    keys_done = time.monotonic()
    quotient.release_isotropic_transports(lines)
    releases.append(time.monotonic() - keys_done)
    carries.append(carry_done - carry_start)
    keys.append(keys_done - carry_done)
    if position < 10 or (position + 1) % band == 0 or position + 1 == PLANES:
        now = time.monotonic()
        steps = 1 if position == 1 else min(band, position - 1)
        print(
            f"  [carry plane {position + 1:6d}/{PLANES}] {now - mark:9.4f} s over {steps} steps"
            f"  carry {1000 * sum(carries[-steps:]) / steps:8.3f} ms and"
            f" {1000 * sum(keys[-steps:]) / steps:8.3f} ms of keys a plane"
            f"  rss {rss_mib():8.1f} MiB"
            f"  transports {int(quotient.retained_isotropic_transport_count())}",
            flush=True,
        )
        mark = now
stage(f"the carry over {len(carries)} planes")
print(
    f"[probe] RESULT phase=carry planes={PLANES} carries={len(carries)}"
    f" carry_ms={1000 * sum(carries) / max(1, len(carries)):.3f}"
    f" keys_ms={1000 * sum(keys) / max(1, len(keys)):.3f}"
    f" wall={time.monotonic() - START:.1f} s rss={rss_mib():.1f} MiB",
    flush=True,
)
