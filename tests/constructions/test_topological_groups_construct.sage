r"""Absolute Galois groups carry their natural profinite topology."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finite_field_absolute_galois_group_is_topological() -> None:
    group = AbsoluteGaloisGroup(GF(5))

    assert group in ProfiniteGroups()
    assert group.is_topological_group()

