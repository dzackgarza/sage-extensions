"""Pushout cocones must agree on the common algebra, unlike coproduct cocones."""

import pytest
from sage_extensions.all import *  # noqa: F401,F403


def test_pushout_mediator_requires_span_compatibility():
    common, left, right = QQ["t"], QQ["x"], QQ["y"]
    t = common.algebra_generator("t")
    x = left.algebra_generator("x")
    y = right.algebra_generator("y")
    f = common.Mor(left)({"t": x**2})
    g = common.Mor(right)({"t": y**3})
    P = Algebras(QQ).Associative().Unital().Commutative().pushout(f, g)
    target = QQ["z"]
    z = target.algebra_generator("z")
    compatible_left = left.Mor(target)({"x": z**3})
    compatible_right = right.Mor(target)({"y": z**2})
    mediator = P.from_pushout_cocone(compatible_left, compatible_right)
    assert mediator * P.left_pushout_map() == compatible_left
    assert mediator * P.right_pushout_map() == compatible_right
    assert mediator(P.left_pushout_map()(x)) == z**3
    assert mediator(P.right_pushout_map()(y)) == z**2

    incompatible_left = left.Mor(target)({"x": z})
    incompatible_right = right.Mor(target)({"y": z})
    assert incompatible_left(f(t)) == z**2
    assert incompatible_right(g(t)) == z**3
    assert z**2 != z**3
    with pytest.raises(ValueError):
        P.from_pushout_cocone(incompatible_left, incompatible_right)
