r"""Affine space over a field has trivial Picard and divisor class groups."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_plane_has_trivial_picard_and_class_groups() -> None:
    plane = AffineSpaces(QQ)(2, names=("x", "y"))

    assert plane.picard_group().order() == 1
    assert plane.class_group().order() == 1
