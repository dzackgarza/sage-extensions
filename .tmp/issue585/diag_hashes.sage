r"""Diagnostic: the two position sets, their hashes and their element types."""

from sage_extensions.all import *  # noqa: F401,F403


def _u_u2_m2():
    return (
        Lattices(ZZ)("U")
        + Lattices(ZZ)(((0, 2), (2, 0)))
        + Lattices(ZZ)(((-2,),))
    )


def _position(cusps, cusp):
    for position, candidate in enumerate(cusps):
        if candidate is cusp:
            return position
    return None


def _edge_positions(incidences, lines, planes):
    return {
        (_position(lines, edge.line_cusp()), _position(planes, edge.plane_cusp()))
        for edge in tuple(incidences)
    }


def _flag_positions(subgroup):
    lines = tuple(subgroup.cusps(1))
    planes = tuple(subgroup.cusps(2))
    pairs = set()
    for flag in subgroup.isotropic_orbit_representatives(2, flag=True):
        line, plane = flag.terms()
        line_cusp = next(cusp for cusp in lines if cusp.transporter_witness(line) is not None)
        plane_cusp = next(cusp for cusp in planes if cusp.transporter_witness(plane) is not None)
        pairs.add((_position(lines, line_cusp), _position(planes, plane_cusp)))
    return pairs


def test_the_hashes() -> None:
    lattice = _u_u2_m2()
    stable = lattice.stable_orthogonal_group()
    lines = tuple(stable.cusps(1))
    planes = tuple(stable.cusps(2))
    right = _flag_positions(stable)
    left = _edge_positions(stable.tits_building_incidence_by_divided_classes(), lines, planes)
    ordered_left = sorted(left, key=str)
    ordered_right = sorted(right, key=str)
    assert False, (
        type(left).__name__,
        type(right).__name__,
        ordered_left == ordered_right,
        left == right,
        [hash(pair) for pair in ordered_left],
        [hash(pair) for pair in ordered_right],
        [[type(part).__name__ for part in pair] for pair in ordered_left],
        [[type(part).__name__ for part in pair] for pair in ordered_right],
    )
