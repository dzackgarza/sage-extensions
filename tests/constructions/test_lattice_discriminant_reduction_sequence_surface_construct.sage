r"""The discriminant-reduction sequence retains its lattice and defining map."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_discriminant_reduction_sequence_retains_source_target_and_map() -> None:
    lattice = Lattices(ZZ)("A2")
    sequence = lattice.discriminant_reduction_sequence()

    assert sequence.lattice() is lattice
    assert sequence.source() is lattice.Aut()
    assert sequence.target() is lattice.discriminant_group().orthogonal_group()
    assert sequence.morphism() is lattice.discriminant_representation()


def test_a2_discriminant_reduction_morphism_has_sequence_endpoints() -> None:
    lattice = Lattices(ZZ)("A2")
    sequence = lattice.discriminant_reduction_sequence()
    morphism = sequence.morphism()

    assert morphism.domain() is sequence.source()
    assert morphism.codomain() is sequence.target()
