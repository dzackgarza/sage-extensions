r"""Affine and projective spaces over fields are varieties."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_line_and_projective_plane_are_varieties(field) -> None:
    line = AffineSpaces(field)(1)
    plane = ProjectiveSpaces(field)(2)

    assert line in Varieties(field)
    assert plane in Varieties(field)
