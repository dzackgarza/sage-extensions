r"""The reflective root system components of a definite lattice, through the public call.

``Lattices(ZZ)(G).reflective_root_system_components()`` returns the components of the
reflective root system together with their multiplicities: on $A_2$ it is
``[("G2", 1)]``, on $A_1$ ``[("A1", 1)]``, on $E_8$ ``[("E8", 1)]``.  The issue records
that every definite lattice raised instead, because the shell enumeration asked a Python
``int`` for its parent ring.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _components(lattice):
    return tuple(
        (name, int(multiplicity))
        for name, multiplicity in lattice.reflective_root_system_components()
    )


def test_a2_has_one_reflective_component_of_type_g2() -> None:
    r"""$A_2$: two square-two roots span $G_2$, the one rank-two component."""
    lattice = Lattices(ZZ)([[2, -1], [-1, 2]])

    assert _components(lattice) == (("G2", 1),)


def test_the_rank_one_root_lattice_has_the_a1_component() -> None:
    r"""$A_1 = \langle 2 \rangle$: a single rank-one component."""
    lattice = Lattices(ZZ)([[2]])

    assert _components(lattice) == (("A1", 1),)


def test_the_e8_lattice_has_the_e8_component() -> None:
    r"""$E_8$: the unimodular even rank-eight root system is one irreducible component."""
    lattice = Lattices(ZZ)("E8")

    assert _components(lattice) == (("E8", 1),)
