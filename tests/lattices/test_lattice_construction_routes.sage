r"""The routes into ``Lattices(ZZ)``: free modules, forms, names, Cartan types and colimits.

- ``Lattices(ZZ)(ZZ^3)`` is the standard Euclidean lattice: identity Gram, determinant 1.
- ``form=`` equips a free module with a given Gram tensor; with the Gram of \(A_2\) the
  result has determinant 3 and is negative definite in this repository's convention.
- ``names=`` names the basis of \(U\); the basis \(e,f\) has \(e^2=f^2=0\), \(ef=1\).
- The Cartan type \(A_3\) presents the root lattice of determinant \(4\) (\(\det A_n = n+1\),
  Conway--Sloane, SPLAG, Ch. 4, section 6).
- ``ZZ^NN`` is the colimit of the \(\mathbf Z^n\): the basis is orthonormal and the rank is
  \(\aleph_0\).  A diagonal Gram on ``ZZ^NN`` changing only the entry at 0 to \(-1\) gives
  \(e_0^2=-1\) and leaves \(e_1^2 = 1\).
- The colimit of the \(A_n\) along \(x\mapsto(x,0)\) has the \(A_n\) pairings on its basis:
  \(e_0^2=-2\), \(e_0e_1=1\), \(e_0e_5=0\).
"""

from sage_extensions.all import *


def test_a_free_module_presents_the_standard_euclidean_lattice() -> None:
    lattice = Lattices(ZZ)(ZZ.free_module(3))
    first, second, _third = lattice.module_generators()

    assert lattice.determinant() == 1
    assert lattice.is_positive_definite()
    assert first * first == 1
    assert first * second == 0


def test_a_free_module_with_the_gram_of_a2() -> None:
    lattice = Lattices(ZZ)(ZZ.free_module(2), form=Lattices(ZZ)("A2").gram_tensor())

    assert lattice.determinant() == 3
    assert lattice.is_negative_definite()
    assert lattice.is_even()


def test_the_named_basis_of_the_hyperbolic_plane() -> None:
    plane = Lattices(ZZ)("U", names=("e", "f"))
    e, f = plane.module_generators()

    assert e * e == 0
    assert f * f == 0
    assert e * f == 1


def test_a_cartan_type_given_as_a_list() -> None:
    r"""\(A_3\) is negative definite here, so \(\det A_3 = (-1)^3 \cdot 4\), as \(|\det A_n| = n + 1\)."""
    lattice = Lattices(ZZ)(["A", 3])

    assert lattice.determinant() == -4
    assert lattice.is_negative_definite()


def test_the_countable_standard_lattice_has_an_orthonormal_basis() -> None:
    lattice = Lattices(ZZ)(ZZ ** NN)
    first = lattice.basis_vector(0)
    second = lattice.basis_vector(1)

    assert first * first == 1
    assert first * second == 0
    assert first.is_root()


def test_the_countable_standard_lattice_has_rank_aleph_zero() -> None:
    assert Lattices(ZZ)(ZZ ** NN).module_rank() == aleph0


def test_the_countable_standard_lattice_base_changes_as_a_lattice() -> None:
    source = Lattices(ZZ)(ZZ ** NN)
    changed = source.base_change(ZZ.fraction_field_map())
    first = changed.basis_vector(0)
    second = changed.basis_vector(1)

    assert changed in Lattices(QQ)
    assert changed.module_rank() == aleph0
    assert first * first == QQ.one()
    assert first * second == QQ.zero()


def test_a_diagonal_gram_changes_only_its_stated_entry() -> None:
    lattice = Lattices(ZZ)((ZZ ** NN).diagonal_gram({0: -1}))

    assert lattice.basis_vector(0) * lattice.basis_vector(0) == -1
    assert lattice.basis_vector(1) * lattice.basis_vector(1) == 1


def test_the_colimit_of_the_root_lattices_a_n() -> None:
    lattices = Lattices(ZZ)
    colimit = lattices.colimit(lambda rank: lattices(["A", rank]))
    first = colimit.basis_vector(0)

    assert first * first == -2
    assert first * colimit.basis_vector(1) == 1
    assert first * colimit.basis_vector(5) == 0
