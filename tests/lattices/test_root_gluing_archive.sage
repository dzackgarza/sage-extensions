r"""Named root-lattice glue reconstructions retained from the archive suite.

Nikulin's isotropic-subgroup/overlattice correspondence and Conway--Sloane's
root-lattice glue tables give the two concrete reconstructions below.  The
assertions are on the live owned inclusions and discriminant classes.
"""

from sage_extensions.all import *


def test_a1_four_has_a_proper_index_two_overlattice_of_d4_genus() -> None:
    source = Lattices.A1 ** 4
    inclusion = source.maximal_overlattice()
    target = inclusion.codomain()

    assert inclusion.index() == 2
    assert target.is_even()
    assert target.genus() == Lattices.D4.genus()


def test_order_five_a4_a4_glue_reconstructs_e8() -> None:
    source = Lattices.A4 + Lattices.A4
    discriminant = source.discriminant_group()
    summands = source.summands()
    first_inclusion = summands[0].embedding().discriminant_inclusion()
    second_inclusion = summands[1].embedding().discriminant_inclusion()
    first = first_inclusion(
        first_inclusion.domain().module_generators()[0]
    )
    second = second_inclusion(
        second_inclusion.domain().module_generators()[0]
    )
    glue_class = first + 2 * second
    glue = discriminant.subobject_generated_by((glue_class,))
    inclusion = discriminant.overlattice_from_isotropic_subobject(glue)
    target = inclusion.codomain()

    invariants = discriminant.invariants()
    assert invariants.cardinality() == 2
    assert invariants[0] == invariants[1] == 5
    assert glue_class.q() == 0
    assert glue.cardinality() == 5
    assert discriminant.orthogonal_quotient(glue).cardinality() == 1
    assert inclusion.index() == 5
    assert target.is_even()
    assert target.is_unimodular()
    assert target.is_isometric(Lattices.E8) is True


def test_d8_isotropic_self_glue_reconstructs_e8() -> None:
    source = Lattices.D8
    inclusion = source.maximal_overlattice()
    target = inclusion.codomain()

    assert inclusion.index() == 2
    assert target.is_even()
    assert target.is_unimodular()
    assert target.twist(-1).enumerate_short_vectors(2).cardinality() == 120
    assert target.is_isometric(Lattices.E8) is True
