r"""The fiber product over Spec R retains its base and projections."""

from sage_extensions.all import *  # noqa: F401,F403


def test_fiber_products_over_the_base(commutative_ring) -> None:
    ring = commutative_ring
    line = AffineSpaces(ring)(1)
    square = Schemes(ring).fiber_product(line.structure_morphism(), line.structure_morphism())

    assert square in FiberProductSchemes(ring)
    assert square.relative_dimension() == 2
    assert square.left_projection().codomain() is line
    assert square.fiber_product_base() == (ring).affine_spectrum()
