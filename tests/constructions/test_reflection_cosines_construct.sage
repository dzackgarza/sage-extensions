r"""Reflection cosines form the exact countable set of Coxeter bond cosines."""

from sage_extensions.all import *  # noqa: F401,F403


def test_reflection_cosines_are_countably_infinite() -> None:
    cosines = reflection_cosines()

    assert cosines.cardinality() == aleph0


def test_reflection_cosines_contain_standard_exact_bond_values() -> None:
    cosines = reflection_cosines()

    assert QQbar(1) / 2 in cosines
    assert (QQbar(1) + QQbar(5).sqrt()) / 4 in cosines


def test_one_third_is_not_a_reflection_cosine() -> None:
    assert QQbar(1) / 3 not in reflection_cosines()
