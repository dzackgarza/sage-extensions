r"""A scheme fiber product retains its pullback construction and universal factorization."""

from sage_extensions.all import *  # noqa: F401,F403


def test_squaring_pullback_retains_projections_and_factors_the_identity_cone() -> None:
    ring = QQ["s"]
    s = ring.algebra_generator("s")
    line = AffineSchemes(QQ)(ring)
    square = line.Mor(line)(ring.Mor(ring)({"s": s**2}))
    identity = line.categorical_identity_morphism()
    pullback = Schemes(QQ).fiber_product(square, square)
    construction = pullback.fiber_product_construction()
    left, right = pullback.fiber_product_projections()
    induced = pullback.from_pullback_cone(identity, identity)

    assert construction.object() is pullback
    assert pullback.left_projection() == left
    assert pullback.right_projection() == right
    assert square * left == square * right
    assert left * induced == identity
    assert right * induced == identity
