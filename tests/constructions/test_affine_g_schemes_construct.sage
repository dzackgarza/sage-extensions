r"""An affine C_2-scheme retains its underlying scheme, action, and quotient data."""

from sage_extensions.all import *  # noqa: F401,F403


def test_sign_involution_on_affine_plane() -> None:
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

    assert acted in AffineGSchemes(group, QQ)
    assert acted.unacted_scheme() is plane
    assert acted.coordinate_algebra() is ring
    assert acted.fixed_subscheme().dimension() == 0
    assert acted.affine_quotient().dimension() == 2
    assert acted.invariant_algebra_inclusion()(acted.invariant_algebra_element(x**2)) == x**2
    assert acted.invariant_algebra_inclusion()(acted.invariant_algebra_element(x * y)) == x * y
