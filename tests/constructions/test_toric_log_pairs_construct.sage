r"""The full toric boundary is anticanonical and gives a toric log Calabi--Yau pair."""

from sage_extensions.all import *  # noqa: F401,F403


def test_full_toric_boundary_is_log_calabi_yau() -> None:
    fans = RationalPolyhedralFans(ZZ.free_module(2))
    plane = fans.projective_space_fan().toric_variety(QQ)
    pair = plane.log_pair()

    assert pair in ToricLogPairs(QQ)
    assert pair.toric_scheme() is plane
    assert pair.is_toric_boundary()
    assert pair.fan() == plane.fan()
    assert pair.is_log_calabi_yau()
