r"""The absolute Galois group of a finite field is a procyclic profinite group."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finite_field_absolute_galois_group_exposes_profinite_structure() -> None:
    group = AbsoluteGaloisGroup(GF(5))
    generators = group.topological_group_generators()
    continuous_endomorphisms = group.continuous_morphisms_to(group)
    identity = continuous_endomorphisms.identity()

    assert group in ProfiniteGroups()
    assert group.is_profinite()
    assert generators.cardinality() == cardinal(1)
    assert identity(generators[0]) == generators[0]

