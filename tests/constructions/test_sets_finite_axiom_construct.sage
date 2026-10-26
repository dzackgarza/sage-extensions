r"""A three-point set lies in the finite refinement of Sets."""

from sage_extensions.all import *  # noqa: F401,F403


def test_three_point_set_is_finite() -> None:
    three = Set((1, 2, 3))

    assert three in Sets().Finite()
    assert three in FiniteSets()
    assert three.cardinality() == cardinal(3)
