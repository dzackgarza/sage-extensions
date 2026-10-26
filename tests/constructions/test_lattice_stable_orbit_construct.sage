r"""On a unimodular lattice splitting two hyperbolic planes, square decides stable primitive-vector orbits."""

from sage_extensions.all import *  # noqa: F401,F403


def test_two_u_stable_orbits_are_decided_by_square() -> None:
    lattice = NamedLattices.U + NamedLattices.U
    first, second, third, fourth = lattice.module_generators()
    left = first + second
    same_square = third + fourth
    opposite_square = first - second

    assert lattice.are_in_one_stable_orbit(left, same_square)
    assert not lattice.are_in_one_stable_orbit(left, opposite_square)
