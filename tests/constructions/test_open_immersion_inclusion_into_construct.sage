r"""Nested distinguished opens expose the induced open immersion between them."""

from sage_extensions.all import *  # noqa: F401,F403


def test_dxy_includes_into_dx_in_the_affine_plane() -> None:
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    ring = plane.coordinate_algebra()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    dx = plane.distinguished_open(x)
    dxy = plane.distinguished_open(x * y)
    inclusion = dxy.inclusion_into(dx)

    assert inclusion.domain() is dxy
    assert inclusion.codomain() is dx
    assert dx.inclusion() * inclusion == dxy.inclusion()
