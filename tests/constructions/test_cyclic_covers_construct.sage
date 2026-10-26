r"""A cyclic double cover retains its degree, branch equation, and deck action."""

from sage_extensions.all import *  # noqa: F401,F403


def test_double_cover_of_the_affine_line() -> None:
    line_ring = QQ["x"]
    x = line_ring.algebra_generator("x")
    covers = CyclicCovers(line_ring, 2)
    cover = covers(x**4 - 1)
    z = cover.cover_variable()

    assert cover in covers
    assert covers.cover_degree() == 2
    assert covers.constant_deck_group().order() == 2
    assert z**2 == cover.coordinate_algebra()(x**4 - 1)
    assert cover.dimension() == 1
    assert cover.branch_subscheme().dimension() == 0
    assert cover.ramification_subscheme().dimension() == 0
    assert cover.invariant_algebra() == line_ring
