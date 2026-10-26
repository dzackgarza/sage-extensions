r"""The rank-two hyperbolic plane has no line-plane incidence in its quotient building."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_tits_building_incidence_is_empty() -> None:
    lattice = NamedLattices.U

    assert lattice.tits_building_incidence().cardinality() == cardinal(0)
