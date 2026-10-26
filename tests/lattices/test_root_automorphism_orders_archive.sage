r"""Root-lattice automorphism orders retained from Conway--Sloane.

SPLAG chapter 4 gives the automorphism-group orders below.  It also identifies
``Aut(A_n)={+-1} W(A_n)`` for ``n>=2`` and notes that ``-1`` already lies in
``W(E8)``, so ``Aut(E8)=W(E8)``.
"""

from sage_extensions.all import *

ROOT_AUTOMORPHISM_ORDERS = {
    "A2": 12,
    "A4": 240,
    "D4": 1152,
    "E6": 103680,
    "E7": 2903040,
    "E8": 696729600,
}


def test_root_lattice_automorphism_orders_match_conway_sloane() -> None:
    for name, expected in ROOT_AUTOMORPHISM_ORDERS.items():
        assert Lattices(ZZ)(name).Aut().order() == expected


def test_a_n_automorphism_group_has_twice_the_weyl_order() -> None:
    for rank in (2, 4):
        lattice = Lattices(ZZ)(f"A{rank}")
        weyl = Groups.Weyl(["A", rank])
        assert lattice.Aut().order() == 2 * weyl.order()


def test_e8_automorphism_group_has_the_weyl_order() -> None:
    assert Lattices.E8.Aut().order() == Groups.Weyl(["E", 8]).order()
