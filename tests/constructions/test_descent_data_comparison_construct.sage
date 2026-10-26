r"""Trivial descent compares the presheaf value isomorphically with its Čech equalizer."""

from sage_extensions.all import *  # noqa: F401,F403


def test_trivial_descent_comparison_is_an_isomorphism_from_the_presheaf_value() -> None:
    site = DiscreteCategory(Sets.Δ[0])
    presheaf = site.presheaves().constant_functor(Sets.Δ[1])
    descent = DescentData.trivial(presheaf)
    obj = site(0)
    identity_cover = descent.coverage().family(obj)
    comparison = descent.comparison(identity_cover)

    assert comparison.isomorphism().domain() is presheaf(obj)
