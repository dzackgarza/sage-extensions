r"""The parabolic at a plane that does not split: what is claimed, and what the obstruction is (#331).

At a primitive isotropic plane that does not split off the lattice, the block
equations of D. Dutour Sikirić and K. Hulek, *Moduli of polarised Enriques
surfaces — computational aspects*, J. London Math. Soc. 110 (2024),
arXiv:2302.01679v2, **Theorem 4.9** (`theorem_isotropic_k_planes`), proof,
printed **p. 22**, give integral lifts of plane actions — #326 builds them for
Sterk's $P_2$ of $T_{\mathrm{En}}$ — but they do not show that the lifts returned
*generate* the subgroup of plane actions admitting one.  The paper's own
statement is an algorithm: an integral extension exists only on a finite-index
subgroup ("we could not find a universal construction of such a lattice"), and
their **Alg 1**, section "Integral group algorithms", computes the integral points
of the rational group by a set-stabilizer computation in $GL_n(\mathbb{Z}/d\mathbb{Z})$
plus Schreier's lemma.  No cited statement names a generating set of the
parabolic.

So at $P_2$ the repository reports the two facts it can: the family generated is
a subgroup of the setwise stabilizer, and `is_parabolic_complete()` is False with
`parabolic_obstruction()` naming the missing statement.  This module pins that,
so that a later unit that settles the congruence subgroup has to change the
answer rather than the record.  It asserts no count and no index.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _second_representative(lattice):
    r"""Sterk's $P_2 = \mathbb{Z}(2e_1 + 2e_2 + w) + \mathbb{Z}e_3$, $w$ of norm $-8$.

    H. Sterk, *Compactifications of the period space of Enriques surfaces,
    Part I*, Math. Z. 207 (1991), Proposition 4.6 (p. 29), in the bases
    $(e_1, e_2)$ of $U$ and $(e_3, e_4)$ of $U(2)$ used by Dutour
    Sikirić--Hulek, section 3.6, p. 22.
    """
    basis_elements = list(lattice.module_generators())
    first, second, third = basis_elements[0], basis_elements[1], basis_elements[2]
    w = basis_elements[4] + basis_elements[5]
    assert lattice.q(w) == ZZ(-8)
    return lattice.primitive_isotropic_subobject(2 * first + 2 * second + w, third)


def test_the_plane_that_does_not_split_is_not_claimed_to_be_complete() -> None:
    r"""$P_2$ does not split, and the parabolic there is a subgroup, not the stabilizer.

    The published statement that is missing is a generation one; Dutour
    Sikirić--Hulek, Theorem 4.9 (arXiv:2302.01679v2, printed p. 22), is an
    algorithm for the stabilizer as the integral points of a rational group, so
    `is_parabolic_complete()` stays False at $P_2$ and the obstruction is stated.
    """
    lattice = NamedLattices.TEn
    plane = _second_representative(lattice)

    assert plane.splitting_complement() is None
    assert plane.is_parabolic_complete() is False
    assert bool(plane.parabolic_obstruction()) is True
    assert plane.levi_lift_generators() != ()


def test_the_split_representative_is_completed_by_the_same_construction() -> None:
    r"""$P_1$ splits off $T_{\mathrm{En}}$, and there the parabolic is the stabilizer.

    The split hypothesis is #295's: $L = P_1 \perp \langle e_2, e_4\rangle \perp E_8(-2)$,
    the block `K = b(U, K)` vanishes, and the argument of
    `parabolic_stabilizer_generators` closes.
    """
    lattice = NamedLattices.TEn
    basis_elements = list(lattice.module_generators())
    plane = lattice.primitive_isotropic_subobject(basis_elements[0], basis_elements[2])

    assert plane.splitting_complement() != ()
    assert plane.is_parabolic_complete() is True
