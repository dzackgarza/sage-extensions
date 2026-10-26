r"""Families over the discrete valuation ring ``QQ[t]_(t)``."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_family_xy_equals_t_is_flat_with_torus_generic_fibre_and_nodal_special_fibre() -> None:
    r"""``xy = t`` over ``A = QQ[t]_(t)``: generic fibre ``xy = t`` over ``QQ(t)`` is smooth and
    irreducible (a torus ``G_m``), special fibre ``xy = 0`` over ``QQ`` is the node, two lines.

    Derivation: ``t`` is a nonzerodivisor on ``A[x, y]/(xy - t)`` (flatness over a DVR is
    torsion-freeness, Hartshorne III.9.7); over ``QQ(t)``, ``y = t/x`` gives ``QQ(t)[x, 1/x]``.
    """
    P = QQ['t']
    t = P.gen()
    A = P.localize_at_prime(P.ideal(t))
    B = A['x,y']
    x, y = B.algebra_generator("x"), B.algebra_generator("y")
    family = B.quotient(B.ideal(x * y - t)).affine_spectrum()
    generic = SchemesOverIntegralDomains(A)(family).generic_fiber()
    special = SchemesOverLocalRings(A)(family).special_fiber()

    assert family.structure_morphism().is_flat()
    assert generic.is_smooth()
    assert generic.is_irreducible()
    assert generic.dimension() == 1
    assert not special.is_smooth()
    assert special.is_reduced()
    assert special.irreducible_components().cardinality() == 2
    assert special.dimension() == 1


def test_scalar_killed_family_detects_nonflatness_over_the_same_dvr() -> None:
    r"""``Spec A[z]/(t)`` over ``A = QQ[t]_(t)`` is not flat: it is ``t``-torsion (Hartshorne III.9.7)."""
    P = QQ['t']
    t = P.gen()
    A = P.localize_at_prime(P.ideal(t))
    B = A['z']
    nonflat = B.quotient(B.ideal(B(t))).affine_spectrum()

    assert not nonflat.structure_morphism().is_flat()
    assert SchemesOverIntegralDomains(A)(nonflat).generic_fiber().is_empty()
    assert SchemesOverLocalRings(A)(nonflat).special_fiber().dimension() == 1
