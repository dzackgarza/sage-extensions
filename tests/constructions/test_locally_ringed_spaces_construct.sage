r"""The stalk of an affine plane at the origin is a local ring."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_plane_stalk_at_origin_is_local() -> None:
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    plane = AffineSchemes(QQ)(ring)
    origin = plane.underlying_space()(ring.ideal(x, y))
    stalk = plane.stalk(origin)

    assert plane in LocallyRingedSpaces()
    assert stalk in LocalRings()
    assert stalk.krull_dimension() == 2
    assert stalk.residue_field() == QQ
