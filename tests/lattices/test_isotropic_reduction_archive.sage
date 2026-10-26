r"""Isotropic reductions ``I^perp/I`` of the Enriques lattice ``U + U(2) + E_8(2)``."""

from sage_extensions.all import *


def _enriques_lattice():
    plane = Lattices(ZZ)("U")
    e8 = Lattices(ZZ)("E8")
    return plane + plane.twist(2) + e8.twist(2), plane, e8


def test_reducing_U_plus_U2_plus_E8_2_along_an_isotropic_vector_of_U_gives_E10_2() -> None:
    r"""``e^perp/e = U(2) + E_8(2) = E_10(2)`` for ``e`` isotropic in the first summand ``U``."""
    lattice, plane, e8 = _enriques_lattice()
    e = lattice.module_generator(0)

    reduction = e.isotropic_reduction()

    assert reduction.module_rank() == 10
    assert reduction.is_isometric((plane + e8).twist(2))


def test_reducing_along_the_isotropic_plane_spanned_by_the_first_vectors_of_U_and_U2_gives_E8_2() -> None:
    r"""For ``I = ZZ e + ZZ e'`` with ``e`` in ``U`` and ``e'`` in ``U(2)``, ``I^perp/I = E_8(2)``."""
    lattice, _plane, e8 = _enriques_lattice()
    e, e_prime = lattice.module_generator(0), lattice.module_generator(2)

    reduction = lattice.sublattice_from([e, e_prime]).isotropic_reduction()

    assert reduction.module_rank() == 8
    assert reduction.is_isometric(e8.twist(2))
