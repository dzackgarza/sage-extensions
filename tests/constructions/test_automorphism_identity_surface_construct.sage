r"""The automorphism category exposes its canonical identity automorphism."""

from sage_extensions.all import *  # noqa: F401,F403


def test_set_automorphism_category_identity_is_the_underlying_set_identity() -> None:
    two = Sets.Δ[1]
    automorphisms = Sets().Aut(two)
    identity = automorphisms.identity_automorphism()

    assert identity == automorphisms.one()
    assert identity.forward() == Sets().Mor(two, two).identity()
    assert identity.inverse() == Sets().Mor(two, two).identity()
