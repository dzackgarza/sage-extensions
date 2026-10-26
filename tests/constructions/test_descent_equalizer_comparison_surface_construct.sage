r"""A descent comparison retains its cover, presheaf, equalizer, and isomorphism."""

from sage_extensions.all import *  # noqa: F401,F403


def _identity_descent_comparison():
    site = DiscreteCategory(Sets.Δ[0])
    presheaf = site.presheaves().constant_functor(Sets.Δ[1])
    descent = DescentData.trivial(presheaf)
    obj = site(0)
    cover = descent.coverage().family(obj)
    return presheaf, obj, cover, descent.comparison(cover)


def test_descent_comparison_retains_its_cover_and_presheaf() -> None:
    presheaf, _obj, cover, comparison = _identity_descent_comparison()

    assert comparison.covering_family() is cover
    assert comparison.presheaf() is presheaf


def test_descent_comparison_isomorphism_has_the_cech_equalizer_as_codomain() -> None:
    presheaf, obj, _cover, comparison = _identity_descent_comparison()
    equalizer = comparison.descent_equalizer()
    isomorphism = comparison.isomorphism()

    assert isomorphism.domain() is presheaf(obj)
    assert isomorphism.codomain() is equalizer.equalizer_object()


def test_descent_comparison_alias_has_the_same_forward_and_inverse_endpoints() -> None:
    presheaf, obj, _cover, comparison = _identity_descent_comparison()
    equalizer = comparison.descent_equalizer()
    isomorphism = comparison.comparison()

    assert isomorphism.forward().domain() is presheaf(obj)
    assert isomorphism.forward().codomain() is equalizer.equalizer_object()
    assert isomorphism.inverse().domain() is equalizer.equalizer_object()
    assert isomorphism.inverse().codomain() is presheaf(obj)
