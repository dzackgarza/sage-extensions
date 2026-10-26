r"""Projective n-space has canonical bundle O(-n-1)."""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_canonical_and_anticanonical_bundles() -> None:
    plane = ProjectiveSpaces(QQ)(2)

    assert plane.canonical_bundle() == plane.canonical_line_bundle() == plane.O(-3)
    assert plane.anticanonical_bundle() == plane.anticanonical_line_bundle() == plane.O(3)


def test_canonical_line_bundle_operation_is_owned_by_smooth_schemes() -> None:
    line = AffineSpaces(QQ)(1)

    assert line in Schemes(QQ).Smooth()
    assert line not in ProjectiveSpaces(QQ)
    assert line not in ProductProjectiveSpaces(QQ)
    assert line not in ProjectivePointBlowups(QQ)
    with pytest.raises(AssertionError, match="det\\(Omega\\^1\\)"):
        line.canonical_line_bundle()
