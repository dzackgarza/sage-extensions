r"""Integral group rings of small finite groups."""

from sage_extensions.all import *  # noqa: F401,F403


def test_group_algebra_retains_its_selected_augmentation_by_identity() -> None:
    group = Groups.C(3)
    algebra = Groups().group_algebra(ZZ)(group)
    augmentation = algebra.augmentation()

    assert augmentation is algebra.augmentation()
    assert Modules(ZZ)._augmentation(group) is augmentation
    assert augmentation.domain() is algebra
    assert augmentation.codomain() is ZZ
    assert augmentation.is_group_algebra_augmentation()
    assert augmentation(algebra(group.group_generators()[0])) == ZZ.one()


def test_underlying_module_of_group_algebra_is_the_literal_functor_composite() -> None:
    group = Groups.C(3)
    group_algebra = Groups().group_algebra(ZZ)
    underlying_module = group_algebra.codomain().underlying_module()
    composite = group_algebra.then(underlying_module)

    algebra = group_algebra(group)
    assert underlying_module(algebra) is algebra
    assert composite(group) is algebra
    assert composite(group).augmentation() is algebra.augmentation()


def test_integral_group_ring_is_commutative_exactly_for_an_abelian_group() -> None:
    r"""``ZZ[C_2]`` is commutative; ``ZZ[S_3]`` is not, since ``S_3`` is not abelian."""
    cyclic_algebra = Groups().group_algebra(ZZ)(Groups.C(2))
    symmetric_algebra = Groups().group_algebra(ZZ)(Groups.S(3))

    assert cyclic_algebra.is_commutative() is True
    assert symmetric_algebra.is_commutative() is False


def test_norm_element_of_zz_c4_is_invariant_and_squares_to_four_times_itself() -> None:
    r"""In ``ZZ[C_4]`` with ``N = 1 + g + g^2 + g^3``: ``g N = N`` and ``N^2 = 4N``;
    the inclusion ``C_2 -> C_4``, ``s ↦ g^2``, sends ``1 + s`` to ``1 + g^2``, and
    ``ZZ[C_4]`` has rank ``|C_4| = 4``.  Derivation: ``hN = N`` for each ``h``."""
    group = Groups.C(4)
    g = group.group_generators()[0]
    algebra = Groups().group_algebra(ZZ)(group)
    norm = algebra(group.one()) + algebra(g) + algebra(g**2) + algebra(g**3)

    assert algebra(g) * norm == norm
    assert norm * norm == 4 * norm
    assert norm * norm != norm
    assert algebra.module_rank() == 4

    subgroup = Groups.C(2)
    s = subgroup.group_generators()[0]
    inclusion = subgroup.Mor(group)({s: g**2})
    induced = Groups().group_algebra(ZZ)(inclusion)
    source = Groups().group_algebra(ZZ)(subgroup)
    assert induced(source(subgroup.one()) + source(s)) == algebra(group.one()) + algebra(g**2)
