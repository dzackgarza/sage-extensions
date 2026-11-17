r"""Probe: the two incidence routes and the flag row on U + U(2) + <-2>, side by side."""

import time

START = time.monotonic()

from sage_extensions.all import *  # noqa: F401,F403

lattice = (
    Lattices(ZZ)("U")
    + Lattices(ZZ)(((0, 2), (2, 0)))
    + Lattices(ZZ)(((-2,),))
)


def positions(cusps, cusp):
    for position, candidate in enumerate(cusps):
        if candidate is cusp or candidate == cusp:
            return position
    return None


for label, subgroup in (
    ("Otilde", lattice.stable_orthogonal_group()),
    ("Otilde+", lattice.stable_orthogonal_group().intersection(lattice.O_plus())),
):
    lines = tuple(subgroup.cusps(1))
    planes = tuple(subgroup.cusps(2))
    print(f"[{label}] line cusps {len(lines)}, plane cusps {len(planes)}", flush=True)
    decided = subgroup.tits_building_incidence_by_divided_classes()
    certified = subgroup.tits_building_incidence()
    class_route = {
        (positions(lines, edge.line_cusp()), positions(planes, edge.plane_cusp()))
        for edge in tuple(decided)
    }
    certificate_route = {
        (positions(lines, edge.line_cusp()), positions(planes, edge.plane_cusp()))
        for edge in tuple(certified)
    }
    print(f"[{label}] class route      {sorted(class_route, key=str)}", flush=True)
    print(f"[{label}] certificate route {sorted(certificate_route, key=str)}", flush=True)
    flags = tuple(subgroup.isotropic_orbit_representatives(2, flag=True))
    print(f"[{label}] flag row: {len(flags)} flags", flush=True)
    pairs = set()
    for flag in flags:
        line, plane = flag.terms()
        line_hits = [c for c in lines if c.transporter_witness(line) is not None]
        plane_hits = [c for c in planes if c.transporter_witness(plane) is not None]
        pair = (positions(lines, line_hits[0]) if line_hits else None, positions(planes, plane_hits[0]) if plane_hits else None)
        pairs.add(pair)
        print(
            f"[{label}]   flag -> line cusps {[positions(lines, c) for c in line_hits]}"
            f" plane cusps {[positions(planes, c) for c in plane_hits]}",
            flush=True,
        )
    print(f"[{label}] flag row        {sorted(pairs, key=str)}", flush=True)
    print(
        f"[{label}] agrees: class==certificate {class_route == certificate_route},"
        f" class==flags {class_route == pairs}",
        flush=True,
    )
print(f"[probe] wall {time.monotonic() - START:.1f} s", flush=True)
