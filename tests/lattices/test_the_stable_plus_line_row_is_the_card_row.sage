r"""The stable-plus isotropic-line row of the Enriques period lattice, from the finite double cosets.

For ``N = U ⊕ U(2) ⊕ E8(-2)`` (lattice-database card ``029J``, the library's ``T_En``) and a
subgroup ``Γ = (ρ, sn)^{-1}(H)`` with ``H ≤ O(A_N) × {±1}``, the kernel ``ker(ρ, sn)`` is
normal in ``O(N)``, so the ``Γ``-orbits inside one ``O(N)``-orbit ``O(N)·v`` are the double
cosets

    ``H \\ (ρ, sn)(O(N)) / (ρ, sn)(Stab_{O(N)}(v))``.

That is the finite-quotient splitting of D. Dutour Sikirić and K. Hulek, *Moduli of polarised
Enriques surfaces — computational aspects*, J. London Math. Soc. 110 (2024),
arXiv:2302.01679v2, **Lemma 3.6 (p. 22)**: for ``U ⊂ K`` a normal subgroup and ``H`` another
subgroup of ``G``, the quotient map ``G → G/U`` carries the double coset decompositions of
``G`` by ``(K, H)`` bijectively onto those of ``G/U`` by ``(K/U, H̄)``.  Their proof uses only
that ``KgiH`` is a union of ``U``-cosets, which holds because ``U ⊂ K``; the finite quotient
``O(N)/ker(ρ, sn) ≤ O(A_N) × {±1}`` is what makes the count a finite computation.  The
hypotheses on our pair are exactly theirs: ``U = ker(ρ, sn)`` is the kernel of a homomorphism
and so normal, and it is contained in ``K = Γ`` because ``Γ = (ρ, sn)^{-1}(H)`` contains the
whole kernel.  No generating family of ``Γ``, or of the kernel, is used: the issue's route.

The row this compares against is the card's ``Otilde+`` row by tag — DSH **§3.6, p. 22**: the
space ``Õ⁺(N)\\D_N`` has 528 zero-dimensional cusps (primitive isotropic lines), split by
``O⁺(F₂^10)`` into orbits of lengths 527 and 1.  The ``O`` row is the input side: the two
``O(N)``-orbits of isotropic lines, spanned by ``L₁ = Ze₁`` and ``L₂ = Ze₃`` (DSH §3.6, p. 22;
H. Sterk, *Compactifications of the period space of Enriques surfaces, Part I*, Math. Z. 207
(1991), Propositions 4.5 (p. 28) and 4.6 (p. 29)), whose stabilizer images have indices 1 and
527.

Red today: the row asks the *kernel's* generating family for a sign witness (the spinor
character does not descend to ``O(A_N)``, since the reflection in a vector of square 2 in the
hyperbolic summand of ``N`` lies in ``ker ρ`` with real spinor norm ``-1`` — DSH p. 2), and no
statement supplies one (sage-extensions#17's reading, ``results/issue17-kernel-generation-blocker.md``).
"""

from sage_extensions.all import *  # noqa: F401,F403


def _enriques_period_lattice():
    r"""``N = U ⊕ U(2) ⊕ E8(-2)``, rank 12 and signature ``(2, 10)``."""
    return NamedLattices.TEn


def _stable_plus(lattice):
    r"""``Õ⁺(L) = ker(ρ, sn)``, retained with complete character data.

    ``ρ: O(L) → O(A_L)`` is the discriminant representation and ``sn`` the real spinor norm
    (Gritsenko--Hulek--Sankaran, arXiv:0810.1614v1, §1, equation (2): ``Õ⁺(L) = Õ(L) ∩ O⁺(L)``).
    """
    orthogonal = lattice.Aut()
    trivial = lattice.discriminant_group().orthogonal_group().subgroup_on(())
    stable = lattice.stable_orthogonal_group()
    plus = lattice.O_plus()
    return orthogonal.predicate_subgroup(
        lambda automorphism: automorphism in stable and automorphism in plus,
        "ker(rho, sn)",
        character_data={"discriminant_preimages": (trivial,), "spinor_kernel": True},
        character_data_complete=True,
    )


def test_the_ambient_line_row_is_the_card_o_row() -> None:
    r"""The input side: two ``O(N)``-orbits of primitive isotropic lines, as the card states."""
    lattice = _enriques_period_lattice()
    representatives = tuple(lattice.Aut().isotropic_orbit_representatives(1))

    expected = card("plane_orbits", "029J")["rows"]["O"]["lines"]
    assert cardinal(sum(1 for _ in representatives)) == cardinal(expected)


def test_the_stable_plus_line_row_is_the_card_otilde_plus_row() -> None:
    r"""528 lines for ``Õ⁺(N)``, the card's ``Otilde+`` row, from the double cosets."""
    lattice = _enriques_period_lattice()
    representatives = tuple(_stable_plus(lattice).isotropic_orbit_representatives(1))

    expected = card("plane_orbits", "029J")["rows"]["Otilde+"]["lines"]
    assert cardinal(sum(1 for _ in representatives)) == cardinal(expected)
