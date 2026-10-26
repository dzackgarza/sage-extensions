r"""The involution ``(x, y) -> (-x, -y)`` of ``A^2_Q`` as an affine ``C_2``-scheme.

Claims, each from the definitions: the fixed subscheme is cut out by ``x - (-x) = 2x`` and
``2y``, so it is the reduced origin; a polynomial is invariant exactly when all its monomials
have even degree, so ``Q[x, y]^{C_2} = Q[x^2, xy, y^2]``, which contains ``x^2`` and ``xy`` but not
``x``; the quotient ``Spec Q[x, y]^{C_2}`` is a surface (the invariant ring has the same
transcendence degree as ``Q[x, y]`` since ``Q[x, y]`` is integral over it); ``(x, y) -> x^2 + y^2``
is invariant, so it factors through the quotient map.
"""

from sage_extensions.all import *


def _sign_involution():
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    plane = AffineSchemes(QQ)(ring)
    group = Groups.C(2)
    negate = plane.Mor(plane)(ring.Mor(ring)({"x": -x, "y": -y}))
    identity = plane.categorical_identity_morphism()
    acted = AffineGSchemes(group, QQ)(plane, lambda element: identity if element == group.one() else negate)
    return ring, x, y, plane, acted


def test_the_sign_involution_remembers_the_plane_it_acts_on() -> None:
    r"""The object is the plane together with the action; forgetting the action returns the plane."""
    ring, x, y, plane, acted = _sign_involution()

    assert acted.unacted_scheme() is plane
    assert acted.coordinate_algebra() is ring


def test_the_fixed_locus_of_the_sign_involution_is_the_origin() -> None:
    r"""``X^{C_2} = V(2x, 2y)``: a point on which ``x`` and ``y`` vanish."""
    ring, x, y, plane, acted = _sign_involution()
    fixed = acted.fixed_subscheme()
    restrict = fixed.inclusion().coordinate_algebra_morphism()

    assert fixed.dimension() == 0
    assert restrict(x) == fixed.coordinate_algebra().zero()


def test_the_invariants_of_the_sign_involution_are_the_even_polynomials() -> None:
    r"""``x^2`` and ``xy`` are invariant; the quotient is two-dimensional."""
    ring, x, y, plane, acted = _sign_involution()
    inclusion = acted.invariant_algebra_inclusion()

    assert inclusion(acted.invariant_algebra_element(x**2)) == x**2
    assert inclusion(acted.invariant_algebra_element(x * y)) == x * y
    assert acted.affine_quotient().dimension() == 2


def test_an_invariant_function_factors_through_the_quotient() -> None:
    r"""``(x, y) -> x^2 + y^2`` is invariant, so it is ``g q`` for a unique ``g`` on the quotient."""
    ring, x, y, plane, acted = _sign_involution()
    line_ring = QQ["t"]
    line = AffineSchemes(QQ)(line_ring)
    norm = Schemes(QQ).Mor(acted, line)(line_ring.Mor(ring)({"t": x**2 + y**2}))

    assert acted.factor_through_affine_quotient(norm) * acted.quotient_morphism() == norm
