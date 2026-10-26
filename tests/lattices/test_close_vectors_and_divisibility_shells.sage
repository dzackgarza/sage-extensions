r"""Lattice points near a rational target, and shells of fixed square and divisibility.

- In \(A_2\) (Gram \(\begin{pmatrix}-2&1\\1&-2\end{pmatrix}\)) the target
  \(t=\tfrac34e_0+\tfrac14e_1\) has \(q(0-t) = q(e_0+e_1-t) = -\tfrac78\) and
  \(q(e_0-t) = -\tfrac38\); every other lattice point has \(|q(x-t)|>1\).  So the points
  with \(q(x-t)\ge-1\) are \(0, e_0, e_0+e_1\).
- In \(\mathbf Z^2\) the centre \((\tfrac12,\tfrac12)\) of the unit square is at square
  distance \(\tfrac12\) from each of its four corners and further from every other point.
- \(D_4 = \{x\in\mathbf Z^4:\sum x_i\text{ even}\}\) with the negated form: its vectors of
  square \(-4\) are \((\pm2,0,0,0)\) and \((\pm1,\pm1,\pm1,\pm1)\), and each pairs evenly with
  every vector of \(D_4\), so all 24 have divisibility 2; the 24 roots have divisibility 1,
  since each root pairs to \(\pm1\) with another root.
"""

from sage_extensions.all import *


def test_the_points_of_a2_near_a_target_close_to_a_simple_root() -> None:
    lattice = Lattices(ZZ)("A2")
    first, second = lattice.module_generators()
    close = lattice.close_vectors((QQ(3) / 4, QQ(1) / 4), -1)

    assert close[first] == QQ(-3) / 8
    assert close[lattice.zero()] == QQ(-7) / 8
    assert close[first + second] == QQ(-7) / 8
    assert not (second in close.index_set())


def test_the_four_corners_of_the_unit_square_are_closest_to_its_centre() -> None:
    lattice = Lattices(ZZ)([[1, 0], [0, 1]])
    first, second = lattice.module_generators()
    close = lattice.close_vectors((QQ(1) / 2, QQ(1) / 2), QQ(1) / 2)

    for corner in (lattice.zero(), first, second, first + second):
        assert close[corner] == QQ(1) / 2
    assert not (first - second in close.index_set())


def test_the_close_vector_families_have_three_and_four_members() -> None:
    root_lattice = Lattices(ZZ)("A2")
    square = Lattices(ZZ)([[1, 0], [0, 1]])

    assert root_lattice.close_vectors((QQ(3) / 4, QQ(1) / 4), -1).cardinality() == 3
    assert square.close_vectors((QQ(1) / 2, QQ(1) / 2), QQ(1) / 2).cardinality() == 4


def test_every_vector_of_square_minus_four_in_d4_has_divisibility_two() -> None:
    lattice = Lattices(ZZ)("D4")
    shell = lattice.vectors_of_square_and_divisibility(-4, 2)

    for vector in lattice.vectors_of_square(-4):
        assert vector in shell
        assert vector.div() == 2
    for root in lattice.vectors_of_square_and_divisibility(-2, 1):
        assert root.q() == -2
        assert root.div() == 1


def test_the_shells_of_d4_by_square_and_divisibility_have_24_members() -> None:
    lattice = Lattices(ZZ)("D4")

    assert lattice.vectors_of_square_and_divisibility(-4, 2).cardinality() == 24
    assert lattice.vectors_of_square_and_divisibility(-2, 1).cardinality() == 24
    assert lattice.vectors_of_square_and_divisibility(-4, 1).cardinality() == 0
