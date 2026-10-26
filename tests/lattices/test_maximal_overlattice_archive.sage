r"""Archive reconciliation for a selected maximal overlattice."""

from sage_extensions.all import *


def test_a1_four_maximal_overlattice_is_the_index_two_d4_genus_extension() -> None:
    source = Lattices.A1 ** 4
    inclusion = source.maximal_overlattice()
    target = inclusion.codomain()

    assert inclusion.domain() is source
    assert inclusion.index() == 2
    assert target.is_even()
    assert target.genus() == Lattices.D4.genus()


def test_the_discriminant_form_of_a1_four_has_a_unique_maximal_isotropic_subgroup() -> None:
    r"""\(A_{A_1^4}=(\mathbb Z/2)^4\) with \(q(\tfrac12 e_i)=-\tfrac12\bmod 2\mathbb Z\).

    A sum of \(k\) distinct classes has \(q=-k/2\), which is \(0\bmod 2\) only for
    \(k=4\); so the only nonzero isotropic class is \(\tfrac12(e_1+\dots+e_4)\), and
    the maximal isotropic subgroup is unique, of order 2 (its overlattice is \(D_4\)).
    """
    discriminant = (Lattices.A1 ** 4).discriminant_group()
    maximal = discriminant.maximal_isotropic_subgroups()

    assert maximal.cardinality() == 1
    (subgroup,) = maximal
    assert subgroup.cardinality() == 2
