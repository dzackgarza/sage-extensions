r"""Hyperbolic lattices: the bound on root lengths and Vinberg's algorithm on \(II_{9,1}\).

- A root \(r\) of a nondegenerate lattice \(L\) satisfies \(2b(x,r)/q(r)\in\mathbf Z\) for
  every \(x\), so \(q(r)\) divides twice the exponent of the discriminant group.  The
  exponent is 1 for the unimodular \(U\oplus E_8\), 2 for \(U\oplus A_1\) and 3 for
  \(U\oplus A_2\); the possible lengths \(|q(r)|\) are the divisors of 2, 4 and 6.
- \(A_2\) is definite, so it is not hyperbolic.
- The reflection group of \(II_{9,1} = U\oplus E_8\) has a fundamental polyhedron with 10
  walls, and the autochronous automorphism group is that reflection group
  (Conway--Sloane, SPLAG, Ch. 27, section 2 and Fig. 27.1).  The polyhedron has an ideal
  vertex, since \(U\) contains isotropic vectors, so it is not compact.
- In \(U\) with timelike \(t = e+f\) (square 2) the isotropic vectors are the multiples of
  \(e\) and \(f\), and \(b(e,t)=b(f,t)=1\); those with \(|b(v,t)|\le1\) are \(\pm e,\pm f\) and 0.
"""

import pytest

from sage_extensions.all import *


def test_the_possible_root_lengths_divide_twice_the_discriminant_exponent() -> None:
    plane = Lattices(ZZ)("U")
    e10 = HyperbolicLattices(ZZ)(plane + Lattices(ZZ)("E8"))
    with_a1 = HyperbolicLattices(ZZ)(plane + Lattices(ZZ)("A1"))
    with_a2 = HyperbolicLattices(ZZ)(plane + Lattices(ZZ)("A2"))

    for length in (1, 2):
        assert length in e10.possible_root_lengths()
    assert not (4 in e10.possible_root_lengths())
    for length in (1, 2, 4):
        assert length in with_a1.possible_root_lengths()
    for length in (1, 2, 3, 6):
        assert length in with_a2.possible_root_lengths()
    assert not (4 in with_a2.possible_root_lengths())


def test_a_definite_lattice_is_not_hyperbolic() -> None:
    with pytest.raises(AssertionError):
        HyperbolicLattices(ZZ)(Lattices(ZZ)("A2"))


def test_vinberg_finds_the_ten_walls_of_ii_9_1() -> None:
    e10 = HyperbolicLattices(ZZ)(Lattices(ZZ)("U") + Lattices(ZZ)("E8"))

    assert e10.is_reflective()
    assert e10.vinberg_simple_roots().cardinality() == 10
    for root in e10.vinberg_simple_roots():
        assert root.q() == -2
    assert not e10.is_cocompact()


def test_the_isotropic_vectors_of_u_of_height_at_most_one() -> None:
    plane = HyperbolicLattices(ZZ)(Lattices(ZZ)("U"))
    first, second = plane.module_generators()
    isotropic = plane.isotropic_elements_below_height(first + second, 1)

    for vector in (first, second, -first, -second):
        assert vector in isotropic
    assert not (2 * first in isotropic)
