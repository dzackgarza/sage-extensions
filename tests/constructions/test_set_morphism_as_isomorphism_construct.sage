r"""A finite set bijection determines the corresponding isomorphism in the core."""

from sage_extensions.all import *  # noqa: F401,F403


def test_transposition_as_isomorphism_has_the_bijection_and_its_inverse() -> None:
    two = Sets.Δ[1]
    swap = Sets().Mor(two, two)(lambda point: two(1 - int(point)))
    isomorphism = swap.as_isomorphism()

    assert isomorphism in Sets().Core().Mor(two, two)
    assert isomorphism.forward() == swap
    assert isomorphism.inverse() == swap
