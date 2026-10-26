r"""Archived involution predicate on live lattice isometries."""

from sage_extensions.all import *




def test_A2_coxeter_element_is_not_an_involution() -> None:
    lattice = Lattices(ZZ)("A2")
    first_root, second_root = lattice.module_generators()
    coxeter = lattice.reflection(first_root) * lattice.reflection(second_root)

    assert coxeter * coxeter != lattice.O().one()
    assert not coxeter.is_involution()
