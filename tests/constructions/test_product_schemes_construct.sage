r"""Products of schemes retain their indexed factors and projections."""

from sage_extensions.all import *  # noqa: F401,F403


def test_products_of_schemes(commutative_ring) -> None:
    ring = commutative_ring
    line = AffineSpaces(ring)(1)
    projective = ProjectiveSpaces(ring)(1)
    plane = Schemes(ring).product((line, line))
    quadric = Schemes(ring).product((projective, projective))
    mixed = line.product(projective)

    assert plane in ProductSchemes(ring)
    assert plane in AffineSchemes(ring)
    assert plane.relative_dimension() == cardinal(2)
    assert plane.factors().cardinality() == cardinal(2)
    assert plane.projections().cardinality() == cardinal(2)
    assert plane.projection(0).codomain() is line
    assert quadric in ProductSchemes(ring)
    assert quadric in ProjectiveSchemes(ring)
    assert quadric.relative_dimension() == 2
    assert mixed.relative_dimension() == 2
    assert mixed not in AffineSchemes(ring)
