r"""Orthogonal predicate subgroups expose vector and isotropic orbit transport."""

from sage_extensions.all import *  # noqa: F401,F403


def test_pell_lattice_norm_one_vectors_form_one_orbit() -> None:
    lattice = Lattices(ZZ)([[1, 0], [0, -2]])
    e, f = lattice.module_generators()
    group = lattice.O()
    target = 3 * e + 2 * f
    witness = group.vector_equivalence_witness(e, target)

    assert group.vector_orbit_representatives(1).cardinality() == cardinal(1)
    assert group.vectors_are_equivalent(e, target)
    assert witness(e) == target


def test_special_orthogonal_group_separates_the_two_isotropic_lines_of_u() -> None:
    lattice = Lattices(ZZ)("U")
    special = lattice.SO()
    representatives = special.isotropic_orbit_representatives(1)

    assert representatives.cardinality() == cardinal(2)
    assert not special.isotropic_are_equivalent(
        representatives[0],
        representatives[1],
    )
