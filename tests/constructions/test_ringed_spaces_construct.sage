r"""An affine scheme is a ringed space whose structure sheaf has its coordinate ring."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_plane_is_a_ringed_space() -> None:
    ring = QQ["x,y"]
    plane = AffineSchemes(QQ)(ring)

    assert plane in RingedSpaces()
    assert plane.structure_sheaf().global_sections() is ring
    assert plane.underlying_space() is ring.spectrum()
