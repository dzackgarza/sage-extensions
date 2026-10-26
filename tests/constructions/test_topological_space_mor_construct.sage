r"""Topological-space Mor objects contain continuous maps and compose them."""

from sage_extensions.all import *  # noqa: F401,F403


def test_identity_and_constant_map_of_the_sierpinski_space() -> None:
    space = TopologicalSpaces().an_object()
    morphisms = TopologicalSpaces().Mor(space, space)
    identity = morphisms.identity()
    constant_one = morphisms(lambda _point: space(1))

    assert identity.parent() is morphisms
    assert identity(space(0)) == space(0)
    assert identity(space(1)) == space(1)
    assert constant_one(space(0)) == space(1)
    assert constant_one(space(1)) == space(1)
    assert constant_one * identity == constant_one
