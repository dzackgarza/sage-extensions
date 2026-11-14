r"""Rational scalars act on ``L tensor QQ`` from either side, and division is that action.

``L tensor_ZZ QQ`` is a ``QQ``-vector space; ``QQ`` is commutative, so the
left and right actions agree, and ``v / r`` is ``r^{-1} v`` for ``r != 0``
(Bourbaki, Algebra I, Ch. II, Section 1.1).  Regression for sage-extensions#150.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_left_right_and_division_by_a_rational_agree() -> None:
    space = Lattices(ZZ)("A2").base_change(ZZ.fraction_field_map())
    vector = tuple(space.module_generators())[0]
    for scalar, inverse in ((1/2, 2), (2, 1/2), (-3/5, -5/3), (QQ(7), QQ(1/7)), (ZZ(3), QQ(1/3))):
        assert scalar * vector == vector * scalar
        assert vector / scalar == inverse * vector
        assert vector / scalar == vector * inverse
