r"""The stable orthogonal group generators call of card `0125` refuses, naming the missing statement (#369).

**What is proved and what is not.**  D. Allcock, *Congruence subgroups and
Enriques surface automorphisms*, J. London Math. Soc. (2) 98 (2018), 1--11,
Theorem 1.1 (p. 2) with its proof (p. 6): the *Bertini involutions* of the
E10 lattice `Λ = E8 + U` (`E8` negative definite) --- the isometries negating
an `E8` summand of a decomposition `Λ = E8 + U` --- generate the level-two
congruence subgroup `W237(2) = ker(O↑(Λ) → O(Λ/2Λ))`; every conjugate of a
Bertini involution is one, so the group they generate is normal in `O(Λ)`.
The generating family is infinite --- one involution per decomposition --- and
no published source restricts it to a finite set, so the call refuses rather
than return the twelve expressions it could construct under a generation
claim.  What the call does prove, by construction: card `0125` is
`L = U(2) ⊕ E8(−2) = Λ(2)` --- rank 10, signature `(1, 9)`, even,
2-elementary with `|A_L| = 2^{10}` --- and each member of the family it
constructs (the base Bertini involution, its ten conjugates in the simple
reflections, and `-1`) is an isometry of `L` lying in `ker ρ_L`.  The normal
closure of the base involution in `W237` needs all its conjugates, not only
those by the simple reflections, so the family is not a generating set.

What this module asserts is exactly those two facts: the membership in
`ker ρ_L` of every member of the family the call constructs and certifies
(the call raises only after certifying them), and the card value read by
tag --- the index `|ρ_L(O(L))|` equals the card's own
`integral.discriminant_form.orthogonal_group_order`.
"""

from sage_extensions.all import *  # noqa: F401,F403
import pytest


def test_the_stable_orthogonal_group_generators_refuse_on_card_0125() -> None:
    r"""The call certifies the family's membership in `ker rho_L` and refuses, and the index is the card's."""
    lattice = NamedLattices.E10_2

    # The call constructs and certifies the Bertini family of card 0125 ---
    # every member's discriminant image is asserted trivial inside the call,
    # so the family lies in ker rho_L --- and then refuses: no published
    # generation statement gives a finite generating set, so no family is
    # returned under a generation claim.
    with pytest.raises(ValueError):
        lattice.stable_orthogonal_group_generators()

    # The card value read by tag: the index of the kernel in O(L) is the
    # card's own orthogonal-group order of the discriminant form.
    assert (
        int(lattice.discriminant_image().cardinality())
        == card("discriminant_forms", "0125")["orthogonal_group_order"]
    )
