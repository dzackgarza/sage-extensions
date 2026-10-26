r"""The canonical and anticanonical bundles of toric projective plane come from their divisors."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_canonical_bundle_is_the_bundle_of_its_canonical_divisor() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)

    assert plane.canonical_divisor() == -3 * plane.hyperplane_divisor()
    assert plane.canonical_line_bundle() == plane.invertible_sheaf_of_divisor(
        plane.canonical_divisor()
    )
    assert plane.canonical_bundle() == plane.canonical_line_bundle()


def test_projective_plane_anticanonical_bundle_is_the_negative_canonical_bundle() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)

    assert plane.anticanonical_line_bundle() == plane.invertible_sheaf_of_divisor(
        -plane.canonical_divisor()
    )
    assert plane.anticanonical_bundle() == plane.anticanonical_line_bundle()
