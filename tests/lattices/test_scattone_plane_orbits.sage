r"""The Scattone plane rows of the rank-21 cards, through the public calls.

``6JRX`` ($\Lambda_2 = U^2 \oplus E_8(-1)^2 \oplus \langle-2\rangle$) and ``6JRY``
($\Lambda_4$, the same with $\langle-4\rangle$) state, keyed by subgroup and certified
with their citations:

- ``O``: the orbits of primitive isotropic planes — J. Scattone, *On the
  compactification of moduli spaces for algebraic K3 surfaces*, Mem. AMS 374 (1987),
  Proposition 5.4.7 with Corollary 5.4.8(2), p. 78 (the bijection
  $E \mapsto E^\perp/E$ from the $O(L_k)$-orbits of primitive isotropic planes onto the
  classes $G(k)$ of the genus of $\langle-2k\rangle \oplus E_8(-1)^2$), together with
  §6.2, p. 97, (6.2.1) for $G(1)$ and §6.3, p. 100, for $G(2)$;
- ``O+``: the same plane counts, §6, p. 94.

These numbers are **not** restated here.  They are the cards' own rows, read by tag
through ``card_plane_orbit_row`` from ``tests/cards/lattice-database-enriques.json``,
which ``tests/cards/refresh_lattice_database_enriques.py`` generates from
``dzackgarza/lattice-database`` at database commit
``587d56febe5856d54c6bc9fc023fa5a425f76bfb``.  The cards certify the rows
(``integral.primitive_orbits``: ``6JRX``
``10326525e21ed937f866e6f77476a56decd775a91f1670b4eca32c2df47cf546``, ``6JRY``
``eba45974e533209118987f193c471e877519717395fa1bdb2076d70e25f9b5e1``), so a
disagreement is a defect of the call or of the card, and never of this file.

Each test is split per card and per subgroup so one specimen's cost cannot hide
another's result, and every returned plane is asserted primitive of rank two and
totally isotropic through the lattice's own pairing, so a wrong object cannot pass by
count alone.
"""

from sage_extensions.all import *  # noqa: F401,F403

#: The two cards and the $k$ of their $\langle-2k\rangle$ summand; the counts are theirs.
_CASES = (
    ("6JRX", 1),
    ("6JRY", 2),
)


def _card_lattice(k):
    r"""$\Lambda_{2k} = U^2 \oplus E_8(-1)^2 \oplus \langle-2k\rangle$, rank 21."""
    return (
        Lattices(ZZ)("U")
        + Lattices(ZZ)("U")
        + Lattices(ZZ)("E8")
        + Lattices(ZZ)("E8")
        + Lattices(ZZ)([[-2 * k]])
    )


def _planes_are_primitive_isotropic_rank_two(planes, lattice) -> None:
    for plane in planes:
        assert plane.module_rank() == cardinal(2)
        assert plane.is_primitive() is True
        for left_label in plane.module_generating_set():
            for right_label in plane.module_generating_set():
                assert lattice.b(
                    plane.inclusion()(plane.module_generator(left_label)),
                    plane.inclusion()(plane.module_generator(right_label)),
                ) == ZZ(0)


def test_the_card_inputs_are_the_published_rank_21_lattices() -> None:
    r"""Rank 21, signature $(2,19)$, determinants $-2$ and $-4$, the cards' symbols."""
    for tag, k in _CASES:
        lattice = _card_lattice(k)
        assert lattice.module_rank() == cardinal(21)
        signature = lattice.signature_pair()
        assert signature.first() == cardinal(2)
        assert signature.second() == cardinal(19)
        assert lattice.determinant() == ZZ(-2 * k)


def test_6jrx_has_the_cards_plane_orbits_under_o() -> None:
    r"""``6JRX``'s ``O`` row: four primitive isotropic plane orbits."""
    lattice = _card_lattice(1)
    planes = lattice.Aut().isotropic_orbit_representatives(2)
    assert planes.cardinality() == cardinal(card_plane_orbit_row("6JRX", "O"))
    _planes_are_primitive_isotropic_rank_two(planes, lattice)


def test_6jry_has_the_cards_plane_orbits_under_o() -> None:
    r"""``6JRY``'s ``O`` row: nine primitive isotropic plane orbits."""
    lattice = _card_lattice(2)
    planes = lattice.Aut().isotropic_orbit_representatives(2)
    assert planes.cardinality() == cardinal(card_plane_orbit_row("6JRY", "O"))
    _planes_are_primitive_isotropic_rank_two(planes, lattice)


def test_6jrx_has_the_cards_plane_orbits_under_o_plus() -> None:
    r"""``6JRX``'s ``O+`` row: four plane orbits (§6, p. 94)."""
    lattice = _card_lattice(1)
    planes = lattice.O_plus().isotropic_orbit_representatives(2)
    assert planes.cardinality() == cardinal(card_plane_orbit_row("6JRX", "O+"))
    _planes_are_primitive_isotropic_rank_two(planes, lattice)


def test_6jry_has_the_cards_plane_orbits_under_o_plus() -> None:
    r"""``6JRY``'s ``O+`` row: nine plane orbits (§6, p. 94)."""
    lattice = _card_lattice(2)
    planes = lattice.O_plus().isotropic_orbit_representatives(2)
    assert planes.cardinality() == cardinal(card_plane_orbit_row("6JRY", "O+"))
    _planes_are_primitive_isotropic_rank_two(planes, lattice)
