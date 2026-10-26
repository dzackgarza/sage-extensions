r"""The Hodge structure of the Fermat quartic K3 surface.

Source: Barth, Hulek, Peters, Van de Ven, *Compact Complex Surfaces*, 2nd ed.,
VIII.3: a K3 surface has `h^{2,0} = h^{0,2} = 1`, `h^{1,1} = 20`, `b_2 = 22`.
"""

from sage_extensions.all import *


def _fermat_quartic():
    space = ProjectiveSpaces(QQ)(3)
    x0, x1, x2, x3 = space.homogeneous_coordinate_generators()
    return space.closed_subscheme(x0**4 + x1**4 + x2**4 + x3**4)


def test_fermat_quartic_has_hodge_numbers_one_twenty_one() -> None:
    r"""`h^{2,0} = h^{0,2} = 1`, `h^{1,1} = 20`, and they sum to `b_2 = 22`."""
    hodge = SmoothQuarticK3CompleteIntersections(QQ)(_fermat_quartic()).hodge_structure()

    assert hodge.hodge_number(2, 0) == 1
    assert hodge.hodge_number(0, 2) == 1
    assert hodge.hodge_number(1, 1) == 20
    assert hodge.hodge_number(1, 0) == 0
    assert hodge.betti_number(2) == 22


def test_fermat_quartic_polarization_is_the_hyperplane_class_of_square_four() -> None:
    r"""The polarization is `c_1(\mathcal{O}(1))`, with `h^2 = \deg X = 4`."""
    quartic = _fermat_quartic()
    polarization = SmoothQuarticK3CompleteIntersections(QQ)(quartic).hodge_structure().polarization_class()

    assert polarization == quartic.first_chern_class(quartic.O(1))
    assert polarization.b(polarization) == 4
