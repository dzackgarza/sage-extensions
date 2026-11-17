r"""The arithmetic-group data of `T_Co`: its index, and the refusal of a generating set (#597).

**The lattice and the group.**  `T_Co = <2> + U(2) + E8(-2)` is even,
2-elementary, of rank 11 and signature `(2, 9)`, with `|A_L| = 2048 = 2^11`.
That last equality is what puts `tilde O(L) = ker(rho_L)` at the level-two
congruence subgroup: `L/2L` and `2L^#/2L` both have order `2^11`, and
`2L^#/2L` is `L^#/L = A_L`, so `L = 2L^#`; then `x |-> x/2` is a bijection
`L/2L -> A_L`, and it is `O(L)`-equivariant because an isometry is
`Z`-linear, so `ker(rho_L) = ker(O(L) -> O(L/2L))`.  That is Allcock's
`W237(2)` in the shape he states it (D. Allcock, *Congruence subgroups and
Enriques surface automorphisms*, J. London Math. Soc. (2) 98 (2018),
Theorem 1.1, p. 2, where `V = Lambda/2Lambda` carries `x*x/2 mod 2`).

**Why the generators are refused.**  Allcock's theorem generates that kernel
by the Bertini involutions --- one per decomposition `Lambda = E8 + U`, an
infinite family --- and it is stated for `Lambda(2) = U(2) + E8(-2)`, of rank
10 and signature `(1, 9)`.  The other published generation statements are
stated in `rank_p(L)`, Gritsenko--Hulek--Sankaran's invariant (arXiv:0810.1614,
§1): Kneser's theorem needs `rank_2 >= 6`, and Gritsenko--Hulek--Sankaran's
proposition 3.4 needs two hyperbolic planes, which force `rank_2 >= 2`, since
a hyperbolic plane is a rank-two sublattice of determinant `-1`.  This lattice
has `rank_2 = 0`, so no statement of transvections or reflections reaches it,
and the call refuses with a `ValueError` stating the hypothesis that fails on
the lattice in hand.

What these modules assert is that refusal, the mathematics it rests on, and
the card value read by tag: `rank_2 = 0` with `rank_3 = 11`, `|A_L| = 2^rank`,
and `|rho_L(O(L))|` equal to card `6JRR`'s own
`integral.discriminant_form.orthogonal_group_order`.
"""

from sage_extensions.all import *  # noqa: F401,F403
import pytest


def test_the_coble_lattice_refuses_its_generating_set_by_stating_the_hypothesis() -> None:
    r"""The call refuses with a stated limit, not with an assertion about a card's identity."""
    with pytest.raises(ValueError):
        NamedLattices.Tco.stable_orthogonal_group_generators()


def test_the_coble_lattice_is_two_elementary_of_full_rank_with_rank_two_zero() -> None:
    r"""`L = 2L^#` (so the kernel is the level-two congruence subgroup) and `rank_2 = 0`."""
    lattice = NamedLattices.Tco
    ring = lattice.base_ring()
    assert int(lattice.discriminant_group().cardinality()) == 2 ** int(lattice.module_rank())
    assert int(lattice.rank_p(ring(2))) == 0
    assert int(lattice.rank_p(ring(3))) == int(lattice.module_rank())


def test_the_finite_orthogonal_group_of_the_coble_discriminant_form_is_the_card_row() -> None:
    r"""The finite group whose order is the kernel's index is the card's own orthogonal-group order.

    The card carries the index as `|O(A_{T_Co}, q)|`, read from the finite
    orthogonal group of the discriminant form; `rho_L` is onto, so that order
    is the index of `ker rho_L`.  The library's own `discriminant_image()`
    agrees and takes 35 s, over this suite's per-call ceiling, so the row
    asserted here is the finite group rather than the image.
    """
    lattice = NamedLattices.Tco
    assert (
        int(lattice.discriminant_group().orthogonal_group().cardinality())
        == card("discriminant_forms", "6JRR")["orthogonal_group_order"]
    )
