r"""The sign action on A^2 exposes its fixed ideal and categorical quotient maps."""

from sage_extensions.all import *  # noqa: F401,F403


def _sign_involution():
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    plane = AffineSchemes(QQ)(ring)
    group = Groups.C(2)
    negate = plane.Mor(plane)(ring.Mor(ring)({"x": -x, "y": -y}))
    identity = plane.categorical_identity_morphism()
    acted = AffineGSchemes(group, QQ)(
        plane,
        lambda element: identity if element == group.one() else negate,
    )
    return ring, x, y, acted


def test_sign_action_fixed_ideal_and_quotient_morphism() -> None:
    ring, x, y, acted = _sign_involution()
    fixed = acted.fixed_ideal()
    quotient = acted.quotient_morphism()

    assert fixed == ring.ideal(2 * x, 2 * y)
    assert quotient.domain() is acted
    assert quotient.codomain() is acted.affine_quotient()


def test_invariant_map_descends_and_factors_through_the_quotient() -> None:
    ring, x, y, acted = _sign_involution()
    target_ring = QQ["t"]
    target = AffineSchemes(QQ)(target_ring)
    invariant = Schemes(QQ).Mor(acted, target)(
        target_ring.Mor(ring)({"t": x**2 + y**2})
    )
    descended = acted.descend_invariant_family(invariant)
    factored = acted.factor_through_affine_quotient(invariant)

    assert descended * acted.quotient_morphism() == invariant
    assert factored * acted.quotient_morphism() == invariant
