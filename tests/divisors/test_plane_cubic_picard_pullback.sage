r"""Pullback of invertible sheaves induces Picard pullback (Hartshorne, II.6)."""

from sage_extensions.all import *


def test_plane_cubic_inclusion_pulls_back_the_hyperplane_class():
    plane = ProjectiveSpaces(QQ)(2)
    x, y, z = plane.homogeneous_coordinate_generators()
    cubic = plane.hypersurface(x**3 + y**3 + z**3)
    picard = Schemes(QQ).picard_functor()
    opposite = picard.domain()
    pullback = picard(opposite.Mor(opposite(plane), opposite(cubic))(cubic.inclusion()))
    target = cubic.picard_group()
    restricted = cubic.inclusion().module_pullback(plane.O(1))

    assert pullback.domain() is plane.picard_group()
    assert pullback.codomain() is target
    assert target.picard_scheme() is cubic
    assert pullback(plane.hyperplane_class()) == target(target.underlying_set()(restricted))
