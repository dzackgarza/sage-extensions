r"""The identity cover retains the canonical Čech equalizer construction."""

from sage_extensions.all import *  # noqa: F401,F403


def _identity_descent_equalizer():
    site = DiscreteCategory(Sets.Δ[0])
    presheaf = site.presheaves().constant_functor(Sets.Δ[1])
    descent = DescentData.trivial(presheaf)
    obj = site(0)
    cover = descent.coverage().family(obj)
    equalizer = DescentEqualizer(descent.coverage(), presheaf, cover)
    return presheaf, obj, cover, equalizer, descent.comparison(cover)


def test_identity_cover_descent_equalizer_retains_its_selected_constructions() -> None:
    _presheaf, _obj, _cover, equalizer, _comparison = _identity_descent_equalizer()

    assert equalizer.equalizer_construction().object() is equalizer.equalizer_object()
    assert equalizer.local_product_construction().object() is not None
    assert equalizer.matching_product_construction().object() is not None


def test_identity_cover_descent_equalizer_maps_have_canonical_endpoints() -> None:
    presheaf, obj, _cover, equalizer, _comparison = _identity_descent_equalizer()
    canonical = equalizer.canonical_map()
    restriction = equalizer.restriction_to_product()
    left, right = equalizer.parallel_maps()

    assert canonical.domain() is presheaf(obj)
    assert canonical.codomain() is equalizer.equalizer_object()
    assert restriction.domain() is presheaf(obj)
    assert restriction.codomain() is equalizer.local_product_construction().object()
    assert left.domain() is restriction.codomain()
    assert right.domain() is restriction.codomain()
    assert left.codomain() is equalizer.matching_product_construction().object()
    assert right.codomain() is equalizer.matching_product_construction().object()


def test_descent_comparison_retains_the_identity_cover_equalizer() -> None:
    _presheaf, _obj, _cover, equalizer, comparison = _identity_descent_equalizer()

    assert comparison.descent_equalizer().covering_family() == equalizer.covering_family()
    assert comparison.descent_equalizer().equalizer_object() is equalizer.equalizer_object()
