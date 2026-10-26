r"""Affine and projective lines over fields are curves."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_and_projective_lines_are_curves(field) -> None:
    affine_line = AffineSpaces(field)(1)
    projective_line = ProjectiveSpaces(field)(1)

    assert affine_line in Curves(field)
    assert projective_line in Curves(field)
    assert affine_line.dimension() == 1
    assert projective_line.dimension() == 1
