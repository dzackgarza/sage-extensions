r"""Affine space has polynomial coordinates and the expected finite-field points."""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_space_over_every_commutative_ring(commutative_ring) -> None:
    ring = commutative_ring
    plane = AffineSpaces(ring)(2, names=("x", "y"))

    assert plane in AffineSpaces(ring)
    assert plane in AffineSchemes(ring)
    assert plane in SmoothSchemes(ring)
    assert plane in Schemes(ring)
    assert plane.relative_dimension() == cardinal(2)
    assert plane.coordinate_ring() in Algebras(ring).Associative().Unital().Commutative()
    assert plane.coordinate_ring().krull_dimension() == ring.krull_dimension() + 2
    assert (plane in IntegralSchemes(ring)) == (ring in IntegralDomains())
    assert plane.scheme_base_ring() is ring
    assert plane.structure_morphism().codomain() == ring.affine_spectrum()


@pytest.mark.parametrize(
    "dimension, size, count",
    [(1, 5, 5), (2, 5, 25), (1, 4, 4), (2, 4, 16), (1, 27, 27)],
)
def test_affine_space_point_counts_over_finite_fields(dimension, size, count) -> None:
    field = GF(size)

    assert AffineSpaces(field)(dimension).point_count() == count
    assert AffineSpaces(field)(dimension).point_count(2) == size ** (2 * dimension)
