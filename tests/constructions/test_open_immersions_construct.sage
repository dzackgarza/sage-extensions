r"""A distinguished open retains its open immersion and localization datum."""

from sage_extensions.all import *  # noqa: F401,F403


def test_distinguished_open_of_x_in_the_affine_plane() -> None:
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    plane = AffineSchemes(QQ)(ring)
    open_set = plane.distinguished_open(x)

    assert open_set in OpenImmersions(plane)
    assert open_set.inclusion().codomain() is plane
    assert open_set.inclusion().is_open_immersion()
    assert open_set.is_distinguished_open()
    assert open_set.distinguished_open_element() == x
