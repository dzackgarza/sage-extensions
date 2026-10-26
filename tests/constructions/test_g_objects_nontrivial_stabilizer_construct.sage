r"""The nontrivial stabilizer locus of the sign action on A^2 is the origin."""

from sage_extensions.all import *  # noqa: F401,F403


def test_sign_action_nontrivial_stabilizer_is_origin() -> None:
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
    stabilizer = acted.nontrivial_stabilizer_subscheme()
    restrict = stabilizer.inclusion().coordinate_algebra_morphism()

    assert stabilizer.dimension() == 0
    assert restrict(x) == stabilizer.coordinate_algebra().zero()
    assert restrict(y) == stabilizer.coordinate_algebra().zero()
