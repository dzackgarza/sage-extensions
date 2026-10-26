r"""Regular polytopes from their Schläfli symbols and their symmetry Coxeter groups.

The symmetry group of the regular polytope ``{p_1, ..., p_{n-1}}`` is the Coxeter group with
linear diagram whose consecutive bonds are ``p_1, ..., p_{n-1}`` (Coxeter, *Regular
Polytopes*, §11.5 and Table I): the cube ``{4,3}`` has group ``B_3`` of order 48, the
24-cell ``{3,4,3}`` has ``F_4``, the pentagon ``{5}`` the dihedral group of order 10.
"""

from sage_extensions.all import *


def test_the_cube_has_the_linear_coxeter_diagram_4_3() -> None:
    r"""``{4,3}``: Coxeter matrix with ``m_{12} = 4``, ``m_{23} = 3`` and ``m_{13} = 2``."""
    cube = RegularPolytopes().from_schlafli_symbol("{4,3}")

    assert tuple(cube.schlafli_symbol()) == (4, 3)
    assert cube.symmetry_coxeter_diagram().coxeter_matrix() == CoxeterDiagrams().from_coxeter_matrix(
        [[1, 4, 2], [4, 1, 3], [2, 3, 1]]
    ).coxeter_matrix()


def test_the_twenty_four_cell_has_the_f4_diagram() -> None:
    r"""``{3,4,3}``: the linear diagram with bonds ``3, 4, 3``, which is ``F_4``."""
    cell = RegularPolytopes().from_schlafli_symbol("{3,4,3}")

    assert cell.symmetry_coxeter_diagram().coxeter_matrix() == CoxeterDiagrams().from_coxeter_matrix(
        [[1, 3, 2, 2], [3, 1, 4, 2], [2, 4, 1, 3], [2, 2, 3, 1]]
    ).coxeter_matrix()


def test_the_pentagon_has_the_dihedral_diagram_i2_5() -> None:
    r"""``{5}``: two mirrors meeting at angle ``pi/5``."""
    pentagon = RegularPolytopes().from_schlafli_symbol("{5}")

    assert tuple(pentagon.schlafli_symbol()) == (5,)
    assert pentagon.symmetry_coxeter_diagram().coxeter_matrix() == CoxeterDiagrams().from_coxeter_matrix(
        [[1, 5], [5, 1]]
    ).coxeter_matrix()


def test_the_cube_is_three_dimensional() -> None:
    r"""A Schläfli symbol with ``n - 1`` entries names an ``n``-dimensional polytope."""
    cube = RegularPolytopes().from_schlafli_symbol("{4,3}")

    assert cube.dimension() == 3


def test_the_symmetry_group_of_the_cube_has_order_48() -> None:
    r"""``|B_3| = 2^3 3! = 48``."""
    cube = RegularPolytopes().from_schlafli_symbol("{4,3}")

    assert cube.symmetry_group().order() == 48
