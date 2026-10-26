r"""Finite module biproducts retain all injections, projections, and factorizations.

For two free rank-one modules, the direct sum is simultaneously product and
coproduct.  Feeding its own injections or projections into the universal maps
therefore recovers the identity.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _two_lines_biproduct():
    left = ZZ.free_module(1)
    right = ZZ.free_module(1)
    return left, right, Modules(ZZ).biproduct((left, right))


def test_biproduct_retains_factors_injections_and_projections() -> None:
    left, right, biproduct = _two_lines_biproduct()
    factors = biproduct.biproduct_factors()

    assert biproduct in BiproductModules(ZZ)
    assert biproduct.biproduct_factor(0) is left
    assert biproduct.biproduct_factor(1) is right
    assert factors.cardinality() == cardinal(2)
    assert biproduct.left_inclusion() == biproduct.left_injection() == biproduct.injection(0)
    assert biproduct.right_inclusion() == biproduct.right_injection() == biproduct.injection(1)
    assert biproduct.left_projection() == biproduct.projection(0)
    assert biproduct.right_projection() == biproduct.projection(1)
    assert isinstance(biproduct.zero(), biproduct.ElementType)


def test_biproduct_universal_maps_recover_the_identity() -> None:
    _left, _right, biproduct = _two_lines_biproduct()
    injections = (biproduct.injection(0), biproduct.injection(1))
    projections = (biproduct.projection(0), biproduct.projection(1))
    identity = biproduct.Mor(biproduct).identity()

    assert biproduct.from_coproduct_cocone(injections) == identity
    assert biproduct.from_product_cone(projections) == identity
    assert biproduct.from_summands(*injections) == identity
    assert biproduct.to_product(*projections) == identity


def test_biproduct_injection_projection_relations_are_delta_ij() -> None:
    left, right, biproduct = _two_lines_biproduct()
    i0, i1 = biproduct.injection(0), biproduct.injection(1)
    p0, p1 = biproduct.projection(0), biproduct.projection(1)

    assert p0 * i0 == left.Mor(left).identity()
    assert p1 * i1 == right.Mor(right).identity()
    assert p0 * i1 == right.Mor(left).zero()
    assert p1 * i0 == left.Mor(right).zero()
