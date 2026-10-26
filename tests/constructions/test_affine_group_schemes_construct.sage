r"""Roots of unity and the additive group are affine group schemes over the base."""

from sage_extensions.all import *  # noqa: F401,F403


def _generator(group_scheme):
    algebra = group_scheme.scheme().coordinate_algebra()
    label = next(iter(algebra.algebra_generating_set()))
    return algebra.algebra_generator(label)


def test_mu_two_retains_its_group_scheme_structure() -> None:
    mu = AffineGroupSchemes(QQ).roots_of_unity(2)
    t = _generator(mu)

    assert mu in AffineGroupSchemes(QQ)
    assert mu.scheme().dimension() == 0
    assert mu.unit_morphism().coordinate_algebra_morphism()(t) == 1
    assert mu.inverse_morphism().coordinate_algebra_morphism()(t) == t
    assert mu.Mor(mu).identity() * mu.Mor(mu).identity() == mu.Mor(mu).identity()


def test_additive_group_is_one_dimensional() -> None:
    additive = AffineGroupSchemes(QQ).additive_group()

    assert additive in AffineGroupSchemes(QQ)
    assert additive.scheme().dimension() == 1
    assert additive.unit_morphism().coordinate_algebra_morphism()(_generator(additive)) == 0
