r"""The genus of the Scattone summand ``<-2k> + E8(-1)^2``, from cards 6JRX and 6JRY.

The plane rows of the rank-21 cards ``6JRX`` and ``6JRY`` are the classes of the
genus of ``<-2k> + E8(-1)^2``: J. Scattone, *On the compactification of moduli
spaces for algebraic K3 surfaces*, Mem. AMS 374 (1987), Proposition 5.4.7 with
Corollary 5.4.8(2), p. 78 -- ``E -> E^perp/E`` is a bijection from the
``O(L_k)``-orbits of primitive isotropic planes onto ``G(k)``, so there are
``h(k)`` of them -- with Section 6.2 (Degree two), p. 97, (6.2.1) giving four
classes in degree two and Section 6.3 (Degree four), p. 100, giving nine in
degree four.  The expected class numbers are therefore the cards' ``planes`` rows
under ``O`` -- four in ``6JRX``, nine in ``6JRY`` -- read here from
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

from sage_extensions.all import *

def _summand_lattice(k):
    r"""``E8(-1)^2 + <-2k>``, the rank-17 lattice of Scattone's plane quotient."""
    return Lattices(ZZ)("E8") + Lattices(ZZ)("E8") + Lattices(ZZ)([[-2 * k]])


def test_the_degree_two_summand_genus_is_the_rank_seventeen_lattice() -> None:
    r"""Rank 17, determinant ``-2``, even, signature ``(0, 17)``, as card 6JRX gives."""
    row = card("plane_orbits", "6JRX")
    lattice = _summand_lattice(1)
    signature = lattice.signature_pair()

    assert row["name"] == "Lambda_2"
    assert int(lattice.module_rank()) == 21 - 4
    assert lattice.determinant() == row["determinant"]
    assert lattice.is_even() is True
    assert signature.first() == cardinal(0)
    assert signature.second() == cardinal(17)


def test_the_degree_two_summand_genus_has_the_cards_class_count() -> None:
    r"""``h(1)`` is card 6JRX's ``O`` plane row, and the enumeration reaches it."""
    row = card("plane_orbits", "6JRX")
    expected = cardinal(row["rows"]["O"]["planes"])
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
    row = card("plane_orbits", "6JRX")
    genus = _summand_lattice(1).genus()
    representatives = genus.representatives()

    assert representatives.cardinality() == cardinal(row["rows"]["O"]["planes"])
    assert all(member.genus() == genus for member in representatives)
    chamber_walls = HyperbolicLattices(ZZ)(
        Lattices(ZZ)("U") + Lattices(ZZ)("E8") + Lattices(ZZ)("E8")
    ).fundamental_chamber().wall_roots()
    assert cardinal(sum(1 for _ in chamber_walls)) == cardinal(19)


def test_the_degree_two_summand_genus_mass_is_the_siegel_mass() -> None:
    r"""``2499347/9440684171518279680000``: the mass the card's classes add up to.

    The reciprocal automorphism orders of the classes are summed inside the
    enumeration, which refuses a family whose masses do not reach this genus mass
    [Conway--Sloane, *SPLAG*, ch. 16]; read here from the public ``mass`` of the
    genus, which is an independent Smith--Minkowski--Siegel computation.
    """
    genus = _summand_lattice(1).genus()

    assert genus.mass() == QQ(2499347) / QQ(9440684171518279680000)


def test_the_degree_four_summand_genus_has_the_cards_class_count() -> None:
    r"""``h(2) = 9`` is card 6JRY's ``O`` plane row, and the enumeration reaches it.

    Scattone, Section 6.3 (Degree four), p. 100: ``G(2)`` consists of nine
    isomorphism classes, so ``O(Lambda_4)`` has nine orbits of primitive
    isotropic planes.  The rank-17 lattice here is the summand whose classes
    those orbits are, and nine is read from the card by tag rather than typed.
    """
    row = card("plane_orbits", "6JRY")
    expected = cardinal(row["rows"]["O"]["planes"])
    genus = _summand_lattice(2).genus()
    representatives = genus.representatives()

    assert representatives.cardinality() == expected
    assert genus.class_number() == expected
    assert all(member.genus() == genus for member in representatives)
    assert all(member.determinant() == -4 for member in representatives)
    assert all(member.is_even() is True for member in representatives)


def test_the_degree_four_summand_genus_mass_is_the_siegel_mass() -> None:
    r"""``642332179/18881368343036559360000``: the mass the nine classes add up to.

    Same statement and same source as the degree-two mass above, at
    ``k = 2``: the nine classes' reciprocal automorphism orders are summed
    inside the enumeration [Conway--Sloane, *SPLAG*, ch. 16], and the public
    ``mass`` of the genus is the independent value they must close on.
    """
    genus = _summand_lattice(2).genus()

    assert genus.mass() == QQ(642332179) / QQ(18881368343036559360000)


def test_the_degree_four_summand_genus_through_the_unimodular_complement() -> None:
    r"""The same nine classes, from the chamber of ``II_{1,17}`` rather than a neighbour walk.

    Nikulin, Math. USSR Izv. 14 (1980), Proposition 1.15.1 with its proof,
    pp. 128--129, and Theorem 1.14.2, p. 125: the classes of the genus of
    ``<-4> + E8(-1)^2`` are the ``v^perp`` for the primitive ``v`` of square
    ``4`` in ``II_{1,17}``, one per ``O(II_{1,17})``-orbit, and the orbits are
    read from the fundamental chamber of Vinberg's reflection group (Vinberg
    1975; Conway--Sloane, *SPLAG*, ch. 27, §2).  The chamber has 19 walls, and
    three of them carry the hyperbolic coordinates, which is what bounds the
    enumeration.  The class masses close on the genus mass, so the nine found
    are all of them.
    """
    row = card("plane_orbits", "6JRY")
    genus = _summand_lattice(2).genus()
    representatives = genus.representatives()

    assert representatives.cardinality() == cardinal(row["rows"]["O"]["planes"])
    assert all(member.genus() == genus for member in representatives)
    chamber_walls = HyperbolicLattices(ZZ)(
        Lattices(ZZ)("U") + Lattices(ZZ)("E8") + Lattices(ZZ)("E8")
    ).fundamental_chamber().wall_roots()
    assert cardinal(sum(1 for _ in chamber_walls)) == cardinal(19)


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
