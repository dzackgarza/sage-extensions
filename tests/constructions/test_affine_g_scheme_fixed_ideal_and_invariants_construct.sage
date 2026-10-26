r"""The sign action on A^2 has fixed ideal (x,y) and its quotient uses the retained invariant algebra."""

from sage_extensions.all import *  # noqa: F401,F403


def test_sign_involution_fixed_ideal_and_invariant_algebra() -> None:
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
    invariants = acted.invariant_algebra()

    assert acted.fixed_ideal() == ring.ideal(x, y)
    assert acted.invariant_algebra_inclusion().domain() is invariants
    assert acted.affine_quotient().coordinate_algebra() is invariants
