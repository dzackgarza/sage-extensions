r"""The integral cohomology of the Fermat quartic K3 surface.

Source: Barth, Hulek, Peters, Van de Ven, *Compact Complex Surfaces*, 2nd ed.,
VIII.3: `H^2(X, \mathbb{Z})` of a K3 surface is the even unimodular lattice
`3U \oplus 2E_8(-1)` of signature `(3, 19)`, and `H^1 = H^3 = 0`.
"""

from sage_extensions.all import *


def _fermat_quartic():
    space = ProjectiveSpaces(QQ)(3)
    x0, x1, x2, x3 = space.homogeneous_coordinate_generators()
    return space.closed_subscheme(x0**4 + x1**4 + x2**4 + x3**4)


def test_quartic_middle_cohomology_is_the_k3_lattice_and_betti_numbers_are_1_0_22_0_1() -> None:
    quartic = _fermat_quartic()
    middle = quartic.integral_cohomology(2)
    signature = middle.signature_pair()

    assert middle.module_rank() == 22
    assert signature.first() == 3
    assert signature.second() == 19
    assert middle.is_even()
    assert middle.is_unimodular()
    assert middle.is_isomorphic(NamedLattices.LK3)
    assert quartic.integral_cohomology(0).module_rank() == 1
    assert quartic.integral_cohomology(1).module_rank() == 0
    assert quartic.integral_cohomology(3).module_rank() == 0
    assert quartic.integral_cohomology(4).module_rank() == 1


def test_quartic_hyperplane_class_is_primitive_of_square_four() -> None:
    r"""`h = c_1(\mathcal{O}(1))` has `h^2 = 4` and is primitive (a line `\ell` on the
    Fermat quartic has `h \cdot \ell = 1`); `c_1(\mathcal{O}(2)) = 2h`."""
    quartic = _fermat_quartic()
    h = quartic.first_chern_class(quartic.O(1))

    assert h.b(h) == 4
    assert h.is_primitive()
    assert quartic.first_chern_class(quartic.O(2)) == 2 * h


def test_quartic_cup_square_of_the_hyperplane_class_is_four_points() -> None:
    r"""`h \smile h = 4 [\mathrm{pt}]` in `H^4(X, \mathbb{Z}) \cong \mathbb{Z}`, and
    `1 \smile h = h`."""
    quartic = _fermat_quartic()
    h = quartic.first_chern_class(quartic.O(1))
    point_class = quartic.fundamental_class_of_a_point()
    unit = quartic.integral_cohomology(0).one()

    assert h.cup(h) == 4 * point_class
    assert unit.cup(h) == h
