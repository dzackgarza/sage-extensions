r"""The basic open D(f) in affine space is its distinguished open D(f)."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_plane_basic_open_is_the_distinguished_open() -> None:
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    x = plane.coordinate_ring().algebra_generator("x")

    assert plane.basic_open(x) == plane.distinguished_open(x)
