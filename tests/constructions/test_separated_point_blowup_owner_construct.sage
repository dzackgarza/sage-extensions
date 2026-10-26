r"""Point blowups are owned by separated schemes, not by projective spaces."""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_point_blowup_uses_the_existing_represented_case() -> None:
    plane = ProjectiveSpaces(QQ)(2)
    point = plane.point_morphism((1, 1, 1))

    blowup = plane.point_blowup(point)

    assert blowup in ProjectivePointBlowups(QQ)
    assert blowup.blowup_source() is plane


def test_affine_plane_inherits_point_blowup_and_reaches_the_algorithm_frontier() -> None:
    plane = AffineSpaces(QQ)(2)
    point = plane.point_morphism((0, 0))

    assert plane in Schemes(QQ).Separated()
    assert plane not in ProjectiveSpaces(QQ)
    assert hasattr(plane, "point_blowup")
    with pytest.raises(AssertionError, match="Rees-algebra construction"):
        plane.point_blowup(point)
