r"""The genus of the Scattone summand ``<-2k> + E8(-1)^2``, from card 6JRX.

The plane rows of the rank-21 cards ``6JRX`` and ``6JRY`` are the classes of the
genus of ``<-2k> + E8(-1)^2``: J. Scattone, *On the compactification of moduli
spaces for algebraic K3 surfaces*, Mem. AMS 374 (1987), Proposition 5.4.7 with
Corollary 5.4.8(2), p. 78 -- ``E -> E^perp/E`` is a bijection from the
``O(L_k)``-orbits of primitive isotropic planes onto ``G(k)``, so there are
``h(k)`` of them -- with Section 6.2 (Degree two), p. 97, (6.2.1) giving four
classes in degree two.  The expected class number is therefore the card's
``planes`` row under ``O``, read here from
``tests/cards/lattice-database-enriques.json`` by tag, the same way the Enriques
rows of #316 read card ``029J`` and card ``0128``.

The enumeration is complete by the Siegel mass formula [Conway--Sloane, *SPLAG*,
ch. 16]: the reciprocal automorphism orders of the classes of a genus add up to
its mass, and ``_genus_classes`` refuses a family whose masses do not.  A
returned family of the card's cardinality is therefore a complete one.

``Lattices(ZZ)("E8")`` is negative definite here, i.e. the cards' ``E8(-1)``, so
the summand is ``E8(-1)^2 + <-2k>`` of rank 17 and determinant ``-2k``, the
lattice whose classes Scattone's bijection counts.
"""

import json
from pathlib import Path

from sage_extensions.all import *

ROOT = Path(__file__).resolve().parents[2]
DIGEST_PATH = ROOT / "tests" / "cards" / "lattice-database-enriques.json"


def _card(tag):
    r"""The card's own rows, from the digest refreshed at the pinned database commit."""
    return json.loads(DIGEST_PATH.read_text(encoding="utf-8"))["plane_orbits"][tag]


def _summand_lattice(k):
    r"""``E8(-1)^2 + <-2k>``, the rank-17 lattice of Scattone's plane quotient."""
    return Lattices(ZZ)("E8") + Lattices(ZZ)("E8") + Lattices(ZZ)([[-2 * k]])


def test_the_degree_two_summand_genus_is_the_rank_seventeen_lattice() -> None:
    r"""Rank 17, determinant ``-2``, even, signature ``(0, 17)``, as card 6JRX gives."""
    card = _card("6JRX")
    lattice = _summand_lattice(1)
    signature = lattice.signature_pair()

    assert card["name"] == "Lambda_2"
    assert int(lattice.module_rank()) == 21 - 4
    assert lattice.determinant() == card["determinant"]
    assert lattice.is_even() is True
    assert signature.first() == cardinal(0)
    assert signature.second() == cardinal(17)


def test_the_degree_two_summand_genus_has_the_cards_class_count() -> None:
    r"""``h(1)`` is card 6JRX's ``O`` plane row, and the enumeration reaches it."""
    card = _card("6JRX")
    expected = cardinal(card["rows"]["O"]["planes"])
    genus = _summand_lattice(1).genus()
    representatives = genus.representatives()

    assert representatives.cardinality() == expected
    assert genus.class_number() == expected
    assert all(member.genus() == genus for member in representatives)
    assert all(member.determinant() == -2 for member in representatives)
    assert all(member.is_even() is True for member in representatives)


def test_the_degree_two_summand_genus_through_the_unimodular_complement() -> None:
    r"""The same four classes, from the chamber of II_{1,17} rather than the neighbour walk.

    Nikulin, Math. USSR Izv. 14 (1980), Proposition 1.15.1 with its proof,
    pp. 128--129, and Theorem 1.14.2, p. 125: the classes are the ``v^perp`` for
    the primitive ``v`` of square ``2`` in ``II_{1,17}``, one per ``O(II_{1,17})``-
    orbit, and the orbits are read from the fundamental chamber of the Vinberg
    reflection group (Vinberg 1975; SPLAG ch. 27).  The chamber has 19 walls, every
    one of square ``-2`` in the model's own form, and the class masses close on the
    genus mass.
    """
    card = _card("6JRX")
    genus = _summand_lattice(1).genus()
    representatives = genus.representatives()

    assert representatives.cardinality() == cardinal(card["rows"]["O"]["planes"])
    assert all(member.genus() == genus for member in representatives)
    chamber_walls = HyperbolicLattices(ZZ)(
        Lattices(ZZ)("U") + Lattices(ZZ)("E8") + Lattices(ZZ)("E8")
    ).fundamental_chamber().wall_roots()
    assert cardinal(len(tuple(chamber_walls))) == cardinal(19)


def test_the_degree_two_summand_genus_mass_is_the_siegel_mass() -> None:
    r"""``2499347/9440684171518279680000``: the mass the card's classes add up to."""
    genus = _summand_lattice(1).genus()

    assert genus.mass() == QQ(2499347) / QQ(9440684171518279680000)


def test_a_definite_genus_with_two_spinor_genera_keeps_its_split() -> None:
    r"""``diag(1, 16, 17)``: two improper spinor genera, and the class numbers keep their partition.

    ``spinor_genus_class_numbers`` reads the split that ``_genus_classes``
    returns, so the entries must be one per improper spinor genus, add up to the
    class number, and name the representative's spinor genus first [CS99,
    Ch. 15, §9.1, Thm. 14].  This genus is definite, which is the branch whose
    enumeration changed, and its partition is held at ``(4, 4)`` -- eight
    classes, four in each spinor genus.
    """
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 16, 0], [0, 0, 17]])
    genus = lattice.genus()

    assert lattice.spinor_genus_count() == cardinal(2)
    numbers = lattice.spinor_genus_class_numbers()

    assert numbers.cardinality() == cardinal(2)
    assert cardinal(sum(int(value) for value in numbers)) == genus.class_number()
    assert all(cardinal(int(value)) >= cardinal(1) for value in numbers)
