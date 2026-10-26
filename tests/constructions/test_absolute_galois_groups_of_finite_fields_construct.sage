r"""The absolute Galois group of a finite field is procyclic, infinite, and topologically singly generated."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finite_field_absolute_galois_group_is_procyclic() -> None:
    group = AbsoluteGaloisGroup(GF(5))
    topological_generators = group.topological_group_generators()
    selected_family = group.topological_generating_family()

    assert group in AbsoluteGaloisGroupsOfFiniteFields()
    assert group.cardinality() == continuum
    assert group.order() == continuum
    assert group.is_abelian()
    assert not group.is_finite()
    assert not group.is_finitely_generated()
    assert topological_generators.cardinality() == cardinal(1)
    assert selected_family.cardinality() == cardinal(1)
    assert selected_family == topological_generators
