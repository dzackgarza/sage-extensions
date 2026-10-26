r"""The additive group of the integers lies in the commutative refinement."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integer_additive_group_is_commutative() -> None:
    category = AdditiveGroups().AdditiveCommutative()

    assert ZZ in category
    assert ZZ(2) + ZZ(3) == ZZ(3) + ZZ(2)

