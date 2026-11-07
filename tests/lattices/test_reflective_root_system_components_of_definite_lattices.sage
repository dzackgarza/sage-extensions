r"""The reflective root system components of a definite lattice, through the public call.

``Lattices(ZZ)(G).reflective_root_system_components()`` returns the irreducible components
of the reflective root system as connected rooted Coxeter diagrams, read in the pair
``(component.label(), component.root_scale())``: ``label()`` is the type's name (``A2``,
``C2``, ``I2(5)`` ...) and ``root_scale()`` is ``q(r)/2`` for a shortest root of the
component.  Each specimen below states the sign of its Gram, so the expected scale follows
from that definition rather than from the returned value:

* ``Lattices(ZZ)("E8")`` is the negative definite form -- this library builds its positive
  counterpart as ``Lattices(ZZ)("E8").twist(-1)`` (``categories/lattices.py``) -- so its
  roots have ``q = -2`` and the scale is ``-1``; the twisted form has scale ``+1``.
* ``<1>`` is odd unimodular: its shortest roots have ``q = 1``, so the scale is ``1/2``.
* ``A2`` and ``<2>`` are even, with shortest roots of ``q = 2`` and scale ``1``.

The issue records that the call raised on every definite lattice instead, because the shell
enumeration asked a Python ``int`` for its parent ring.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _components(lattice):
    r"""The components as ``(label, root scale)``, the documented reading of each diagram."""
    return tuple(
        (component.label(), component.root_scale())
        for component in lattice.reflective_root_system_components()
    )


def test_a2_has_one_reflective_component_of_type_g2() -> None:
    r"""``A2``: two square-two roots span ``G2``, the one rank-two component."""
    lattice = Lattices(ZZ)([[2, -1], [-1, 2]])

    assert _components(lattice) == (("G2", 1),)


def test_the_odd_unimodular_line_has_half_root_scale() -> None:
    r"""``<1>``: shortest roots of ``q = 1``, so ``q(r)/2 = 1/2``."""
    lattice = Lattices(ZZ)([[1]])

    assert _components(lattice) == (("A1", QQ(1) / 2),)


def test_the_even_rank_one_root_lattice_has_root_scale_one() -> None:
    r"""``A1 = <2>``: shortest roots of ``q = 2``, scale ``1``."""
    lattice = Lattices(ZZ)([[2]])

    assert _components(lattice) == (("A1", 1),)


def test_the_negative_definite_e8_lattice_has_root_scale_minus_one() -> None:
    r"""``E8(-1) = Lattices(ZZ)("E8")``, signature ``(0, 8)``: roots of ``q = -2``, scale ``-1``."""
    lattice = Lattices(ZZ)("E8")

    assert lattice.signature_pair() == signature_pair(0, 8)
    assert _components(lattice) == (("E8", -1),)


def test_the_positive_definite_e8_lattice_has_root_scale_one() -> None:
    r"""``E8 = Lattices(ZZ)("E8").twist(-1)``, signature ``(8, 0)``: roots of ``q = 2``, scale ``1``."""
    lattice = Lattices(ZZ)("E8").twist(-1)

    assert lattice.signature_pair() == signature_pair(8, 0)
    assert _components(lattice) == (("E8", 1),)
