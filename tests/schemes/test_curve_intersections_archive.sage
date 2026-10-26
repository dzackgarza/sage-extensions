r"""Local intersection multiplicities of plane curves.

Gathmann, *Plane Algebraic Curves*, Example 2.13 computes multiplicity ``4`` at
the origin for ``y^2 - x^3`` and ``x^2 - y^3``.  Proposition 2.17 gives
multiplicity ``1`` where the linear parts are independent; at ``(1, 1)`` the two
gradients ``(-3, 2)`` and ``(2, -3)`` are independent.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_two_cusps_meet_with_multiplicity_four_at_the_origin_and_one_at_1_1() -> None:
    r"""``I_0(y^2 - x^3, x^2 - y^3) = 4`` and ``I_{(1,1)} = 1`` (Gathmann Ex. 2.13, Prop. 2.17)."""
    R = QQ['x,y']
    x, y = R.algebra_generator("x"), R.algebra_generator("y")
    plane = R.affine_spectrum()
    first = plane.closed_subscheme(y**2 - x**3)
    second = plane.closed_subscheme(x**2 - y**3)

    origin = plane.point(R.ideal(x, y))
    transverse = plane.point(R.ideal(x - 1, y - 1))

    assert first.intersection_multiplicity(second, origin) == 4
    assert first.intersection_multiplicity(second, transverse) == 1
