r"""Affine invariant quotients carry their canonical scalar-extension comparison."""

from sage_extensions.all import *  # noqa: F401,F403


def test_sign_action_quotient_base_change_comparison_has_canonical_endpoints() -> None:
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
    extension = QQ.Mor(GF(5))(lambda rational: GF(5)(rational))
    comparison = acted.quotient_base_change_comparison(extension)

    assert comparison.domain() is acted.base_change(extension).affine_quotient()
    assert comparison.codomain() is acted.affine_quotient().base_change(extension)
