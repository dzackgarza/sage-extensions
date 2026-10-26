r"""Lagrangian glue for the rank-one sign pair retained from the archive.

For ``<2> + <-2>`` the diagonal class in the discriminant form is isotropic
and equals its own orthogonal complement.  Nikulin's correspondence therefore
gives an index-two even unimodular overlattice.
"""

from sage_extensions.all import *


def test_rank_one_sign_pair_diagonal_glue_is_lagrangian_and_unimodular() -> None:
    lattice = Lattices(ZZ)([[2]]) + Lattices(ZZ)([[-2]])
    form = lattice.discriminant_group()
    first, second = form.module_generators()
    diagonal = first + second
    glue = form.subobject_generated_by((diagonal,))
    inclusion = form.overlattice_from_isotropic_subobject(glue)
    target = inclusion.codomain()

    assert diagonal.q() == 0
    assert glue.cardinality() == 2
    assert form.orthogonal_quotient(glue).cardinality() == 1
    assert inclusion.index() == 2
    assert target.is_even()
    assert target.is_unimodular()
