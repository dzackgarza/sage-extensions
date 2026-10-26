r"""The fibre product of two schemes over the base scheme.

``Spec R`` is terminal in ``Sch/R``, so ``X x_{Spec R} Y`` is ``Spec(A tensor_R B)``;
the diagonal induced by the pair ``(id, id)`` composes with each projection back to
the identity.
"""

from sage_extensions.all import *


def _line_over(ring):
    r"""``A^1_R`` built as a spectrum, with its square over ``Spec R``."""
    line = (ring.polynomial_ring("x")).affine_spectrum(base_ring=ring)
    structure = line.structure_morphism()
    return line, line.scheme_category().fiber_product(structure, structure)


def test_the_affine_line_squared_over_the_integers_is_the_affine_plane() -> None:
    r"""`\mathbb{Z}[x] \otimes_{\mathbb{Z}} \mathbb{Z}[x] \cong \mathbb{Z}[x_1, x_2]`."""
    line, plane = _line_over(ZZ)

    assert plane.is_isomorphic(AffineSpaces(ZZ)(2))
    assert plane.relative_dimension() == 2
    assert plane.left_projection().codomain() is line
    assert plane.right_projection().codomain() is line


def test_the_diagonal_is_the_map_induced_by_the_pair_of_identities() -> None:
    line, plane = _line_over(QQ)
    identity = line.categorical_identity_morphism()

    diagonal = plane.from_pullback_cone(identity, identity)
    left_projection, right_projection = plane.fiber_product_projections()
    construction = diagonal.cone_construction()

    assert construction.target() is plane
    assert construction.legs()[0] is identity
    assert construction.legs()[1] is identity
    assert diagonal.domain() is line
    assert diagonal.codomain() is plane
    assert left_projection * diagonal == identity
    assert right_projection * diagonal == identity


def test_fiber_of_the_first_projection_over_the_origin_is_an_affine_line() -> None:
    line, plane = _line_over(QQ)
    algebra = line.coordinate_algebra()
    x = algebra.algebra_generator("x")
    origin = line.closed_subscheme(x)
    first_projection = plane.fiber_product_projections()[0]
    fiber = first_projection.codomain().scheme_category().fiber_product(
        first_projection,
        origin.inclusion(),
    )

    assert fiber.fiber_product_base() is line
    assert fiber.left_projection().codomain() is plane
    assert fiber.right_projection().codomain() is origin
    assert fiber.relative_dimension() == 1
    assert first_projection * fiber.left_projection() == (
        origin.inclusion() * fiber.right_projection()
    )
