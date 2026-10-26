r"""Cyclic groups lie in the commutative refinement of owned groups."""

from sage_extensions.all import *  # noqa: F401,F403


def test_cyclic_six_is_abelian() -> None:
    group = Groups.C(6)
    generator = group.group_generators()[0]

    assert group in AbelianGroups()
    assert group.is_abelian()
    assert generator * generator**2 == generator**2 * generator

