r"""The support of a hyperplane divisor on projective plane is a curve."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_hyperplane_support_has_dimension_one() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    support = plane.torus_invariant_divisor_support_subscheme(plane.hyperplane_divisor())

    assert support.relative_dimension() == 1
