r"""An abelian group carries the canonical integer action through its endomorphism ring."""

from sage_extensions.all import *  # noqa: F401,F403


def test_cyclic_four_integer_action_factors_through_endomorphisms() -> None:
    group = Groups.C(4)
    generator = group.group_generators()[0]
    endomorphisms = group.endomorphism_ring()
    action = group.scalar_action()
    doubling = action(ZZ(2))

    assert action.domain() is ZZ
    assert action.codomain() is endomorphisms
    assert doubling(generator) == generator * generator
