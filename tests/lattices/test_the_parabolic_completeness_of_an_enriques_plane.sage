r"""The parabolic at a plane that does not split: the three factors, and their decision (#331, #366).

At a primitive isotropic plane $P$ the parabolic is
$P_I = \mathrm{Stab}_{O(L)}(P)$, and it maps onto a subgroup
$M \subseteq \GL(P) \times O(P^\perp/P)$ with kernel the unipotent radical $U_I$.  A
generating family is the whole parabolic exactly when it contains $U_I$ and its image is
$M$, by the correspondence between the subgroups containing a normal subgroup and the
subgroups of the quotient (Milne, *Group Theory*, v4.01, Theorem 1.47 printed p. 22, with
Corollary 1.48 printed p. 23).  `parabolic_completeness_decision()` computes the three
factors of that statement — the radical by its parameter lattice (#365), the plane actions
of the members trivial on $P^\perp/P$, and the quotient images of the members that fix $P$
pointwise — and `is_parabolic_complete()` is `True` exactly when all three are one.

At Sterk's $P_2$ of $T_{\mathrm{En}}$, which does *not* split off the lattice, all three
hold, so the parabolic there is generated and `parabolic_obstruction()` is `None`; at
$P_1$, which does split, the block equations force the answer directly.  What the block
equations of Dutour Sikirić–Hulek, Theorem 4.9 (arXiv:2302.01679v2, printed pp. 33--34), give
on their own is the *lifts* of plane actions — their **Alg 1** computes the integral points
of the rational group by a set-stabilizer computation in $GL_n(\mathbb{Z}/d\mathbb{Z})$ plus
Schreier's lemma, which is the whole of $M$ and not a generating set of it — so the
generation here rests on the three computed factors and not on that algorithm.

This module pins the decision at both representatives, and no count or index is typed.
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


def test_the_plane_that_does_not_split_is_complete_by_its_three_factors() -> None:
    r"""$P_2$ does not split, and its parabolic is generated anyway — decided, not assumed.

    The three factors of `parabolic_completeness_decision()` are compared with the answer
    the predicate gives: the radical's own index, the plane actions of the members trivial
    on $P_2^\perp/P_2$, and the quotient images of the members that fix the plane
    pointwise.  All three being one *is* the statement that the family generates the
    parabolic, so the predicate is `True` and there is no obstruction left to state.
    """
    lattice = NamedLattices.TEn
    plane = _second_representative(lattice)

    assert plane.splitting_complement() is None
    assert plane.unipotent_radical_index() == cardinal(1)
    assert plane.levi_plane_action_index(trivial_on_quotient=True) == cardinal(1)
    assert plane.levi_quotient_image_index(trivial_on_plane=True) == cardinal(1)
    assert plane.is_parabolic_complete() is True
    assert plane.parabolic_obstruction() is None
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


def test_the_plane_actions_at_p2_are_all_of_the_general_linear_group() -> None:
    r"""Every plane action in $\mathrm{GL}_2(\mathbb{Z})$ occurs at $P_2$.

    The block equation of Dutour Sikirić--Hulek, Theorem 4.9 (arXiv:2302.01679v2,
    printed pp. 33--34), is $P_1 = J Q_1^{-t} J^{-1}$ with $J = b(U, P)$, so a plane
    action $Q_1$ admits an integral lift only if it preserves the row lattice of
    $J^t$.  At $P_2$ the block data is $J = 2 \cdot 1_2$, so that lattice is
    $2\mathbb{Z}^2$ and *no* congruence condition on $Q_1$ follows: the group of
    admissible plane actions is all of $\mathrm{GL}_2(\mathbb{Z})$.  This is what
    `levi_plane_action_index` computes, by exhibiting the two Sanov shears and
    $-1$ among the family's plane actions (Sanov 1947: $\Gamma(2)$ is generated by
    them) and reducing modulo two, where the image is all of
    $\mathrm{GL}_2(\mathbb{F}_2)$; so the index is $1$.

    The same index is asked of the generators that act *trivially on
    $P_2^\perp/P_2$*, because that is the set whose elements are $(M, 1)$ in
    $\mathrm{GL}(P) \times O(P^\perp/P)$: with it the first factor of the Levi
    image is full, and then the Levi image is the whole product
    $\mathrm{GL}_2(\mathbb{Z}) \times H_0$.  Nothing in the family is short of
    the parabolic by a plane action.
    """
    lattice = NamedLattices.TEn
    plane = _second_representative(lattice)

    assert plane.levi_plane_action_index() == cardinal(1)
    assert plane.levi_plane_action_index(trivial_on_quotient=True) == cardinal(1)


def test_the_split_plane_action_has_index_three() -> None:
    r"""At $P_1$ the plane actions are the congruence subgroup $\Gamma^0(2)$, of index three.

    $P_1$ splits, so the block $K = b(U, K)$ vanishes and the lift conditions of
    Dutour Sikirić--Hulek, Theorem 4.9, reduce to the first: $P_1 = J Q_1^{-t}
    J^{-1}$ integral, with $J = \begin{pmatrix}1&0\\0&2\end{pmatrix}$.  That is
    the condition $c \equiv 0 \pmod 2$ on $Q_1 = \begin{pmatrix}a&b\\c&d\end{pmatrix}$,
    i.e. $\Gamma^0(2)$, whose index in $\mathrm{GL}_2(\mathbb{Z})$ is
    $|\mathrm{GL}_2(\mathbb{F}_2)| / |\text{upper triangular}| = 6/2 = 3$.

    The family realises exactly that subgroup, so the index is $3$ and not $1$:
    the two planes differ in this index, and it is the split plane that carries
    the congruence condition.
    """
    lattice = NamedLattices.TEn
    basis_elements = list(lattice.module_generators())
    plane = lattice.primitive_isotropic_subobject(basis_elements[0], basis_elements[2])

    assert plane.levi_plane_action_index() == cardinal(3)
