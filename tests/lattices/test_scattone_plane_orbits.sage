r"""The Scattone plane rows of the rank-21 cards, through the public calls.

``6JRX`` ($\Lambda_2 = U^2 \oplus E_8(-1)^2 \oplus \langle-2\rangle$) and ``6JRY``
($\Lambda_4$, the same with $\langle-4\rangle$) state, keyed by subgroup and certified
with their citations:

- ``O``: 4 and 9 orbits of primitive isotropic planes — Scattone, *On the
  compactification of moduli spaces for algebraic K3 surfaces*, Mem. AMS 374 (1987),
  Prop. 5.4.7 with Cor. 5.4.8(2), p. 78, with §6.2 p. 97 and §6.3 p. 100;
- ``O+``: the same plane counts, 4 and 9 — §6, p. 94.

These are the card's cited rows, not derived here.  Each test is split per card and
per subgroup so one specimen's cost cannot hide another's result, and every returned
plane is asserted primitive of rank two and totally isotropic through the lattice's own
pairing, so a wrong object cannot pass by count alone.
"""

from sage_extensions.all import *  # noqa: F401,F403

# tag, k, expected planes under O and O+
_CASES = (
    ("6JRX", 1, 4),
    ("6JRY", 2, 9),
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
    r"""Rank 21, signature $(2,19)$, determinants $-2$ and $-4$, the cards' genus symbols."""
    for tag, k, _planes in _CASES:
        lattice = _card_lattice(k)
        assert lattice.module_rank() == cardinal(21)
        signature = lattice.signature_pair()
        assert signature.first() == cardinal(2)
        assert signature.second() == cardinal(19)


def test_6jrx_has_four_primitive_isotropic_plane_orbits_under_o() -> None:
    r"""``6JRX``'s certified ``O`` row: four primitive isotropic plane orbits."""
    lattice = _card_lattice(1)
    planes = lattice.Aut().isotropic_orbit_representatives(2)
    assert planes.cardinality() == cardinal(4)
    _planes_are_primitive_isotropic_rank_two(planes, lattice)


def test_6jry_has_nine_primitive_isotropic_plane_orbits_under_o() -> None:
    r"""``6JRY``'s certified ``O`` row: nine primitive isotropic plane orbits."""
    lattice = _card_lattice(2)
    planes = lattice.Aut().isotropic_orbit_representatives(2)
    assert planes.cardinality() == cardinal(9)
    _planes_are_primitive_isotropic_rank_two(planes, lattice)


def test_6jrx_has_four_plane_orbits_under_o_plus() -> None:
    r"""``6JRX``'s certified ``O+`` row: four plane orbits (§6, p. 94)."""
    lattice = _card_lattice(1)
    planes = lattice.O_plus().isotropic_orbit_representatives(2)
    assert planes.cardinality() == cardinal(4)
    _planes_are_primitive_isotropic_rank_two(planes, lattice)


def test_6jry_has_nine_plane_orbits_under_o_plus() -> None:
    r"""``6JRY``'s certified ``O+`` row: nine plane orbits (§6, p. 94)."""
    lattice = _card_lattice(2)
    planes = lattice.O_plus().isotropic_orbit_representatives(2)
    assert planes.cardinality() == cardinal(9)
    _planes_are_primitive_isotropic_rank_two(planes, lattice)
