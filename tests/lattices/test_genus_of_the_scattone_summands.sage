r"""The genus of the Scattone summand ``<-2k> + E8(-1)^2``, closed by the mass.

The plane rows of the rank-21 cards ``6JRX`` and ``6JRY`` are the classes of the
genus of ``<-2k> + E8(-1)^2`` (issue #317): Scattone, *On the compactification
of moduli spaces for algebraic K3 surfaces*, Mem. AMS 374 (1987), Proposition
5.4.7 with Corollary 5.4.8(2), p. 78.  The class number is read off the
enumeration, and the enumeration is complete by the Siegel mass formula
[Conway--Sloane, *SPLAG*, ch. 16]: the reciprocal automorphism orders of the
classes of a genus add up to its mass, and the owner of ``_genus_classes``
refuses to return a class family whose masses do not.  So a returned family of
the stated cardinality is a complete one.

``Lattices(ZZ)("E8")`` is negative definite here, i.e. the cards' ``E8(-1)``, so
the summand is ``E8(-1)^2 + <-2k>`` of rank 17 and determinant ``-2k``, the
lattice whose classes Scattone's bijection counts.
"""

from sage_extensions.all import *


def _summand_lattice(k):
    r"""``E8(-1)^2 + <-2k>``, the rank-17 lattice of Scattone's plane quotient."""
    return Lattices(ZZ)("E8") + Lattices(ZZ)("E8") + Lattices(ZZ)([[-2 * k]])


def test_the_degree_two_summand_genus_is_the_rank_seventeen_lattice() -> None:
    r"""Rank 17, determinant ``-2``, even, signature ``(0, 17)``, as Scattone's ``L_1`` gives."""
    lattice = _summand_lattice(1)
    signature = lattice.signature_pair()

    assert lattice.module_rank() == cardinal(17)
    assert lattice.determinant() == -2
    assert lattice.is_even() is True
    assert signature.first() == cardinal(0)
    assert signature.second() == cardinal(17)


def test_the_degree_two_summand_genus_has_four_classes_by_the_mass() -> None:
    r"""``h(1) = 4``: four classes, each of them in the genus, and the mass closes."""
    lattice = _summand_lattice(1)
    genus = lattice.genus()
    representatives = genus.representatives()

    assert genus.class_number() == cardinal(4)
    assert representatives.cardinality() == cardinal(4)
    assert all(member.genus() == genus for member in representatives)
    assert all(member.determinant() == -2 for member in representatives)
    assert all(member.is_even() is True for member in representatives)


def test_the_degree_two_summand_genus_mass_is_the_siegel_mass() -> None:
    r"""``2499347/9440684171518279680000``: the mass the four classes must add up to."""
    genus = _summand_lattice(1).genus()

    assert genus.mass() == QQ(2499347) / QQ(9440684171518279680000)
