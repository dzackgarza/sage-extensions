r"""The degree-two and degree-four K3 period lattices, as `lattice-database` states them.

The corrected Scattone cards (`dzackgarza/lattice-database`, `main`
`67526965910fe6d4212b23705973e3abd42bcd6c`) state

    tag 6JRX  Lambda_2 = U + U + E8(-1) + E8(-1) + <-2>   rank 21, signature (2,19), det -2
    tag 6JRY  Lambda_4 = U + U + E8(-1) + E8(-1) + <-4>   rank 21, signature (2,19), det -4

both even, with discriminant group $\mathbb Z/2$ and $\mathbb Z/4$, and both carrying
``certifications: integral.primitive_orbits`` digests
(``10326525e21ed9…`` and ``eba45974e53320…``).  Those cards replace versions whose two $E_8$
blocks were stored as $-2\times$ the Cartan matrix; the values asserted here are the cards',
and the invariants below are exactly the ones such a block cannot satisfy: an $E_8$ summand is
unimodular, and the whole lattice's determinant is $-2k$ with the dyadic genus symbol carrying
$2^1$ or $4^1$.

Nothing here counts orbits.  The cards' boundary rows (four and nine primitive isotropic
planes, one isotropic line) are compared with the public orbit calls by the unit that owns
them; a count would not be derived here, and none is written in this file.
"""

from sage_extensions.all import *  # noqa: F401,F403

# (tag, k, card determinant, card genus symbol), read from the two cards.
_CASES = (
    ("6JRX", 1, ZZ(-2), "II_{2,19} (2: 1^20 [2^1]_7)"),
    ("6JRY", 2, ZZ(-4), "II_{2,19} (2: 1^20:[4^1]_7)"),
)


def _period_lattice(k):
    r"""$U \oplus U \oplus E_8(-1) \oplus E_8(-1) \oplus \langle -2k\rangle$.

    ``Lattices(ZZ)("E8")`` is already negative definite (signature $(0,8)$, root scale
    $-1$), so the card's two $E_8(-1)$ summands are two copies of it, not twists.
    """
    return (
        Lattices(ZZ)("U")
        + Lattices(ZZ)("U")
        + Lattices(ZZ)("E8")
        + Lattices(ZZ)("E8")
        + Lattices(ZZ)([[-2 * k]])
    )


def test_the_e8_summand_is_unimodular_which_the_retired_cards_were_not() -> None:
    r"""$E_8(-1)$ is unimodular, determinant $1$; $-2\times$ its Cartan matrix has $256$.

    $-\!C$ negates an $8\times8$ block, so $\det(-C) = (-2)^8\det(C)/2^8 = \det(C) = 1$; the
    retired cards' $-2\times$ Cartan block has determinant $(-2)^8 = 256$.  This is the
    invariant that separates the corrected cards from the retired ones, and it needs no orbit
    enumeration.
    """
    e8 = Lattices(ZZ)("E8")
    assert e8.determinant() == ZZ(1)
    assert e8.signature_pair().first() == cardinal(0)
    assert e8.signature_pair().second() == cardinal(8)


def test_the_degree_two_period_lattice_is_the_card_lattice() -> None:
    r"""``6JRX``: rank $21$, signature $(2,19)$, determinant $-2$, even, $\mathbb Z/2$."""
    tag, k, determinant, genus_symbol = _CASES[0]
    lattice = _period_lattice(k)

    assert lattice.module_rank() == cardinal(21)
    signature = lattice.signature_pair()
    assert signature.first() == cardinal(2)
    assert signature.second() == cardinal(19)
    assert lattice.determinant() == determinant
    assert lattice.is_even() is True
    assert lattice.conway_sloane_genus_symbol() == genus_symbol


def test_the_degree_four_period_lattice_is_the_card_lattice() -> None:
    r"""``6JRY``: the same lattice with $\langle -4\rangle$: determinant $-4$, $\mathbb Z/4$."""
    tag, k, determinant, genus_symbol = _CASES[1]
    lattice = _period_lattice(k)

    assert lattice.module_rank() == cardinal(21)
    signature = lattice.signature_pair()
    assert signature.first() == cardinal(2)
    assert signature.second() == cardinal(19)
    assert lattice.determinant() == determinant
    assert lattice.is_even() is True
    assert lattice.conway_sloane_genus_symbol() == genus_symbol


def test_the_two_cards_differ_only_in_the_orthogonal_line() -> None:
    r"""$\Lambda_2$ and $\Lambda_4$ agree on $U^2 \oplus E_8(-1)^2$ and differ in the last entry.

    Their Gram tensors therefore agree everywhere except the final diagonal entry, which is
    $-2$ against $-4$: the two cards are one family, not two unrelated lattices, and neither
    is the $-2\times E_8$ shape.
    """
    two = _period_lattice(1).gram_tensor()
    four = _period_lattice(2).gram_tensor()
    rank = 21
    last = rank - 1

    for row in range(rank):
        for column in range(rank):
            if (row, column) == (last, last):
                continue
            assert two[row, column] == four[row, column]
    assert two[last, last] == ZZ(-2)
    assert four[last, last] == ZZ(-4)
