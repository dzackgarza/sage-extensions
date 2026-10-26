r"""Absolute Galois groups retain the characteristic and basic profinite structure of the field."""

from sage_extensions.all import *  # noqa: F401,F403


def test_absolute_galois_groups_over_finite_and_rational_fields() -> None:
    finite = AbsoluteGaloisGroup(GF(5))
    rational = AbsoluteGaloisGroup(QQ)

    assert finite in AbsoluteGaloisGroups()
    assert rational in AbsoluteGaloisGroups()
    assert finite.characteristic() == 5
    assert rational.characteristic() == 0
    assert finite.is_abelian()
    assert not rational.is_abelian()
    assert finite.is_profinite()
    assert rational.is_profinite()


def test_absolute_galois_group_generators_are_not_claimed_as_finite_abstract_data() -> None:
    group = AbsoluteGaloisGroup(GF(5))

    assert not group.group_generators_are_computable()
    assert not group.has_computed_group_generators()

