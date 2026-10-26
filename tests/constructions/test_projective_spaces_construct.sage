r"""Projective space is smooth and has the expected finite-field points."""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_space_over_every_commutative_ring(commutative_ring) -> None:
    ring = commutative_ring
    line = ProjectiveSpaces(ring)(1)

    assert line in ProjectiveSpaces(ring)
    assert line in ProjectiveSchemes(ring)
    assert line in SmoothSchemes(ring)
    assert line in Schemes(ring)
    assert line.relative_dimension() == 1
    assert line.is_projective()
    assert (line in IntegralSchemes(ring)) == (ring in IntegralDomains())


@pytest.mark.parametrize(
    "dimension, size, count",
    [(1, 5, 6), (2, 5, 31), (1, 4, 5), (2, 4, 21), (1, 27, 28)],
)
def test_projective_space_point_counts_over_finite_fields(dimension, size, count) -> None:
    field = GF(size)

    assert ProjectiveSpaces(field)(dimension).point_count() == count
