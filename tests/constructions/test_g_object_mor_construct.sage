r"""An equivariant identity is the identity arrow and identity natural transformation of an action."""

from sage_extensions.all import *  # noqa: F401,F403


def test_equivariant_identity_exposes_underlying_arrow_and_transformation() -> None:
    group = Groups.S(3)
    acted = FiniteGSets(group)((1, 2, 3), lambda g, point: g(point))
    identity = acted.Mor(acted).identity()
    arrow = identity.underlying_arrow()
    transformation = identity.natural_transformation()
    object_of_bg = next(iter(group.classifying_category().object_set()))

    assert arrow(1) == 1
    assert transformation.source() == acted.action_functor()
    assert transformation.target() == acted.action_functor()
    assert transformation.component(object_of_bg)(1) == 1

