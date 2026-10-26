r"""The type of the root system of norm-two vectors of an even definite lattice.

Expected values: Conway--Sloane, *Sphere Packings, Lattices and Groups*, 3rd
ed., Ch. 4 (extraction ``references/literature/lattice-research/conway1999sphere.md``).
The minimal vectors of ``A_n``, ``D_n`` and ``E_8`` have norm 2 (§6.1, §7.1,
§8.1) and are the root systems of those names, whose fundamental roots are an
integral basis of the root lattice (§2, Table 4.1).  For an orthogonal sum of
negative definite even lattices, ``b(x+y,x+y) = b(x,x) + b(y,y)`` with both
terms even and nonpositive, so a vector of norm ``-2`` lies in one summand: the
roots of the sum are the union of the roots of the summands.  ``<-4>`` has no
vector of norm ``-2``.  Named lattices here are negative definite
(``Lattices(ZZ)("E8")`` is ``E8(-1)``).

The spelling convention of the type is the one of
``Lattices.ParentMethods.norm_two_root_types``: components joined by ``+``,
``E`` before ``D`` before ``A``, decreasing rank within one letter.
"""

import pytest

from sage_extensions.all import *


def test_two_copies_of_e8_and_a_norm_minus_two_line_give_e8_e8_a1() -> None:
    lattice = Lattices(ZZ)("E8") + Lattices(ZZ)("E8") + Lattices(ZZ)([[-2]])

    assert lattice.norm_two_root_types() == "E8+E8+A1"


def test_d16_and_a_norm_minus_two_line_give_d16_a1() -> None:
    lattice = Lattices(ZZ)("D16") + Lattices(ZZ)([[-2]])

    assert lattice.norm_two_root_types() == "D16+A1"


def test_e8_alone_is_irreducible_of_type_e8() -> None:
    assert Lattices(ZZ)("E8").norm_two_root_types() == "E8"


def test_the_positive_definite_e8_has_the_same_type() -> None:
    assert Lattices(ZZ)("E8").twist(-1).norm_two_root_types() == "E8"


def test_components_are_spelled_e_before_d_whatever_the_summand_order() -> None:
    lattice = Lattices(ZZ)("D10") + Lattices(ZZ)("E7")

    assert lattice.norm_two_root_types() == "E7+D10"


def test_a_summand_without_norm_two_vectors_adds_no_component() -> None:
    lattice = Lattices(ZZ)("E8") + Lattices(ZZ)([[-4]])

    assert lattice.norm_two_root_types() == "E8"


def test_an_isotropic_reduction_answers_as_the_lattice_it_is() -> None:
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("E8") + Lattices(ZZ)([[-2]])

    reduction = lattice.basis_vector(0).isotropic_reduction()

    assert reduction.norm_two_root_types() == "E8+A1"


def test_an_indefinite_lattice_has_no_finite_norm_two_root_system() -> None:
    with pytest.raises(AssertionError):
        Lattices(ZZ)("U").norm_two_root_types()


def test_an_odd_definite_lattice_is_outside_the_operation() -> None:
    with pytest.raises(AssertionError):
        Lattices(ZZ)([[-1, 0], [0, -1]]).norm_two_root_types()
