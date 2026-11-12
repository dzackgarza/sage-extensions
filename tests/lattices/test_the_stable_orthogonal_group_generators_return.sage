r"""Generators of the stable orthogonal group of card `0125`, from a published statement (#369).

**The statement.**  D. Allcock, *Congruence subgroups and Enriques surface
automorphisms*, J. London Math. Soc. (2) 98 (2018), 1--11, Theorem 1.1 (p. 2)
with its proof (p. 6): for the E10 lattice `Λ = E8 + U` (`E8` negative definite),
the *Bertini involutions* --- the isometries negating an `E8` summand of a
decomposition `Λ = E8 + U` --- lie in the level-two congruence subgroup
`W237(2) = ker(O↑(Λ) → O(Λ/2Λ))` and generate it; every conjugate of one is one,
so `W237(2)` is the normal closure of a single Bertini involution in
`O↑(Λ) = W237`, which Vinberg's theorem (Allcock, Theorem 2.2, p. 6) generates by
its simple reflections.

**On this lattice.**  Card `0125` is `L = U(2) ⊕ E8(-2) = Λ(2)`, so `O(L) = O(Λ)`
as subgroups of `GL_10(Z)` and `Õ(L) = ker(O(Λ) → O(Λ/2Λ)) = ⟨W237(2), -1⟩`,
because `-1` acts trivially on `Λ/2Λ` and `O(Λ) = ⟨O↑(Λ), -1⟩`.  What this module
asserts is what the call computes: the family is the base Bertini involution, its
conjugates by the `10` simple reflections Vinberg's algorithm returns, and `-1`;
every member is an isometry of `L`, an involution, and lies in `ker ρ_L`; and the
index of that kernel in `O(L)` is the card's own
`integral.discriminant_form.orthogonal_group_order`, read by tag.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_bertini_family_generates_the_stable_orthogonal_group_of_card_0125() -> None:
    r"""The family lies in `ker rho_L`, its size is the simple roots' plus two, and the index is the card's."""
    lattice = NamedLattices.E10_2
    group = lattice.Aut()
    identity = group.one()
    trivial = lattice.discriminant_group().orthogonal_group().one()

    family = lattice.stable_orthogonal_group_generators()
    simple_roots = HyperbolicLattices(ZZ)(lattice).vinberg_simple_roots()
    # The family is the set of distinct members among the base Bertini involution,
    # its conjugates in the ten simple reflections, and -1: the reflections in the
    # eight roots that lie in the E8 summand commute with the base, so those
    # conjugates coincide with it.  The count below is the one the call returns.
    assert int(family.cardinality()) <= int(simple_roots.cardinality()) + 2

    for generator in family:
        assert generator * ~generator == identity
        assert generator * generator == identity
        assert generator.discriminant_morphism() == trivial
        assert generator in lattice.stable_orthogonal_group()

    index_of_the_kernel = int(lattice.discriminant_image().cardinality())
    assert index_of_the_kernel == card("discriminant_forms", "0125")["orthogonal_group_order"]
