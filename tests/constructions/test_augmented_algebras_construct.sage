r"""An augmented algebra retains its augmentation to the base ring."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integer_group_algebra_is_augmented() -> None:
    group = Groups.C(3)
    algebra = ZZ[group]
    augmentation = algebra.augmentation()

    assert algebra in AugmentedAlgebras(ZZ)
    assert algebra.is_augmented()
    assert isinstance(algebra.one(), algebra.ElementType)
    assert augmentation.codomain() is ZZ
    assert all(augmentation(algebra(g)) == ZZ.one() for g in group)
