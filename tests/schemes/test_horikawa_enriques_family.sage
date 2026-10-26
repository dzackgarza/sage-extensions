r"""The Horikawa Enriques surface as the free quotient of a K3 surface by an involution.

Source for every value: Barth, Hulek, Peters, Van de Ven, *Compact Complex
Surfaces*, 2nd ed., VIII.15 and VIII.19: for an Enriques surface `Y` with K3
cover `\pi: X \to Y`, `e(Y) = 12`, `K_Y` is 2-torsion and nonzero,
`H^2(Y, \mathbb{Z}) = E_{10} \oplus \mathbb{Z}/2` with `E_{10} = U \oplus E_8(-1)`,
`\pi^*` multiplies the form by 2 and has image the invariant lattice
`U(2) \oplus E_8(-2)`, whose orthogonal complement is `U \oplus U(2) \oplus E_8(-2)`.
"""

from sage_extensions.all import *


def test_enriques_surface_is_a_free_double_quotient_of_a_k3_surface() -> None:
    r"""`\pi: X \to Y` is étale of degree 2, `e(X) = 24 = 2 e(Y)`, and `K_Y` has order 2."""
    surface = HorikawaEnriquesSurface()
    quotient = surface.quotient_morphism()
    k3 = quotient.domain()
    canonical = surface.canonical_class()

    assert quotient.codomain() is surface
    assert quotient.degree() == 2
    assert quotient.deck_transformation().fixed_locus().is_empty()
    assert k3.euler_characteristic() == 24
    assert surface.euler_characteristic() == 12
    assert canonical != 0
    assert 2 * canonical == 0


def test_enriques_h2_is_e10_plus_two_torsion_and_pulls_back_to_the_invariant_lattice() -> None:
    r"""`H^2(Y) = E_{10} \oplus \mathbb{Z}/2`; `\pi^*` doubles the form onto the rank-10
    invariant lattice, whose complement has rank 12; both have discriminant group of
    order `2^{10}` (they glue to the unimodular `H^2(X)`)."""
    surface = HorikawaEnriquesSurface()
    quotient = surface.quotient_morphism()
    cohomology = surface.integral_cohomology(2)
    free = cohomology.torsion_free_quotient()
    pullback = quotient.cohomology_pullback(2)
    k3_lattice = pullback.codomain()
    involution = quotient.deck_transformation().cohomology_pullback(2)
    invariant = k3_lattice.invariant_lattice(involution)
    coinvariant = k3_lattice.coinvariant_lattice(involution)

    assert cohomology.torsion_submodule().cardinality() == 2
    assert free.is_isomorphic(NamedLattices.E10)
    assert k3_lattice.is_isomorphic(NamedLattices.LK3)
    assert all(
        pullback(left).b(pullback(right)) == 2 * left.b(right)
        for left in free.module_generators()
        for right in free.module_generators()
    )
    assert all(
        involution(pullback(generator)) == pullback(generator)
        for generator in free.module_generators()
    )
    assert invariant.module_rank() == 10
    assert coinvariant.module_rank() == 12
    assert invariant.discriminant_group().cardinality() == 2**10
    assert coinvariant.discriminant_group().cardinality() == 2**10


def test_enriques_involution_has_trace_minus_two_and_lefschetz_number_zero() -> None:
    r"""On `H^2(X)` the involution has trace `10 - 12 = -2`, so its Lefschetz number is
    `1 - 2 + 1 = 0`, the Euler characteristic of its empty fixed locus."""
    surface = HorikawaEnriquesSurface()
    deck = surface.quotient_morphism().deck_transformation()

    assert deck.cohomology_pullback(2).trace() == -2
    assert deck.lefschetz_number() == 0
    assert deck.fixed_locus().is_empty()
