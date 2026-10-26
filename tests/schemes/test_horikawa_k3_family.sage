r"""The Horikawa K3 surfaces: double covers of `\mathbb{P}^1 \times \mathbb{P}^1` branched in a `(4,4)` curve.

Source: Barth, Hulek, Peters, Van de Ven, *Compact Complex Surfaces*, 2nd ed.,
V.23 (Horikawa's model) and VIII.18; van Geemen and Sarti, *Nikulin involutions
on K3 surfaces*, Math. Z. 255 (2007), section 1 (a symplectic involution has
eight fixed points).  `\tau` is the involution `(x, y) \mapsto (-x, -y)` of the
base, with four fixed points.
"""

from sage_extensions.all import *


def test_tau_splits_the_bidegree_four_four_sections_as_thirteen_plus_twelve() -> None:
    r"""`h^0(\mathcal{O}(4,4)) = 25`; `\tau` fixes the monomials `x_0^a x_1^{4-a} y_0^b y_1^{4-b}`
    with `a + b` even (`3 \cdot 3 + 2 \cdot 2 = 13`) and negates the other 12."""
    family = HorikawaK3Family()
    sections = family.branch_line_bundle().global_sections()
    tau = family.base_involution().action_on_sections(family.branch_line_bundle())

    assert sections.module_rank() == 25
    assert sections.invariant_submodule(tau).module_rank() == 13
    assert sections.anti_invariant_submodule(tau).module_rank() == 12


def test_double_cover_branched_in_an_invariant_four_four_curve_is_a_k3_surface() -> None:
    r"""The branch curve has genus `(4-1)(4-1) = 9`, the cover has
    `K = \pi^*(K_B + \tfrac12 B) = \pi^*\mathcal{O}(0,0) = 0` and
    `e = 2 \cdot 4 - (2 - 2 \cdot 9) = 24`."""
    member = HorikawaK3Family().member()
    cover = member.cover_morphism()
    k3 = cover.domain()

    assert cover.degree() == 2
    assert member.branch_curve().genus() == 9
    assert k3.canonical_class() == 0
    assert k3.euler_characteristic() == 24
    assert k3.irregularity() == 0


def test_the_two_lifts_of_tau_are_a_free_enriques_and_a_symplectic_nikulin_involution() -> None:
    r"""Over each of the four fixed points of `\tau` the cover has two points: one lift
    swaps them and is free, acting by `-1` on `H^0(K_X)`; the other fixes all eight
    and acts by `+1`."""
    member = HorikawaK3Family().member()
    enriques = member.enriques_lift()
    nikulin = member.nikulin_lift()
    identity = enriques.domain().Mor(enriques.domain()).identity()

    assert enriques * enriques == identity
    assert nikulin * nikulin == identity
    assert enriques != nikulin
    assert enriques.fixed_locus().is_empty()
    assert nikulin.fixed_locus().relative_dimension() == 0
    assert nikulin.fixed_locus().length() == 8
    assert enriques.action_on_holomorphic_two_forms() == -1
    assert nikulin.action_on_holomorphic_two_forms() == 1
