r"""The identity of a finite G-set is an injective and surjective equivariant map."""

from sage_extensions.all import *  # noqa: F401,F403


def test_natural_s3_set_identity_is_a_bijective_equivariant_map() -> None:
    group = Groups.S(3)
    acted = FiniteGSets(group)((1, 2, 3), lambda g, point: g(point))
    identity = acted.Mor(acted).identity()
    transformation = identity.natural_transformation()

    assert identity.is_injective()
    assert identity.is_surjective()
    assert identity(1) == 1
    assert transformation.source() == acted.action_functor()
    assert transformation.target() == acted.action_functor()

