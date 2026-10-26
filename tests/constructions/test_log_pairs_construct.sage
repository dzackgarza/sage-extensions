r"""A toric boundary gives a log pair whose log scheme and boundary are retained."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_with_toric_boundary_is_a_log_pair() -> None:
    fans = RationalPolyhedralFans(ZZ.free_module(2))
    plane = fans.projective_space_fan().toric_variety(QQ)
    pair = LogPairs(QQ)(plane, plane.toric_boundary_divisor())

    assert pair in LogPairs(QQ)
    assert pair.log_scheme() is plane
    assert pair.scheme() is plane
    assert pair.boundary_divisor() == plane.toric_boundary_divisor()
    assert pair.log_canonical_divisor() == pair.boundary_divisor_group().zero()
