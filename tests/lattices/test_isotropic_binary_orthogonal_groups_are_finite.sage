r"""The cited split-binary theorem controls finite orthogonal-group placement."""

from sage_extensions.all import *


def test_the_integral_hyperbolic_plane_has_four_orthogonal_isometries() -> None:
    group = Lattices(ZZ)("U").O()

    assert group in Groups().Finite()
    assert group.cardinality() == 4


def test_a_nonsplit_indefinite_binary_group_is_not_placed_finite() -> None:
    lattice = Lattices(ZZ)([[1, 0], [0, -2]])

    assert lattice.O() not in Groups().Finite()


def test_a_definite_rational_plane_is_not_placed_finite() -> None:
    lattice = Lattices(QQ)(2)

    assert lattice.O() not in Groups().Finite()
