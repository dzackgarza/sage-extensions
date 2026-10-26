r"""A scheme fiber product retains the cospan whose pullback it represents."""

from sage_extensions.all import *  # noqa: F401,F403


def test_squaring_pullback_retains_its_defining_cospan() -> None:
    ring = QQ["s"]
    s = ring.algebra_generator("s")
    line = AffineSchemes(QQ)(ring)
    squaring = line.Mor(line)(ring.Mor(ring)({"s": s**2}))
    pullback = Schemes(QQ).fiber_product(squaring, squaring)
    cospan = pullback.fiber_product_cospan()

    assert cospan.apex() is line
    assert cospan.left_leg() == squaring
    assert cospan.right_leg() == squaring
