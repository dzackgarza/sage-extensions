r"""Ordinals form the thin category of represented ordinals under comparison."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finite_and_initial_ordinals_expose_the_category_surface() -> None:
    ordinals = Ordinals()
    two = ordinals(2)
    three = ordinals(3)
    omega = ordinals.initial(0)

    assert two in ordinals
    assert two.cardinality() == cardinal(2)
    assert two.cnf_terms() == ((ordinal(0), ZZ(2)),)
    assert not two.is_initial()
    assert omega.is_initial()
    assert omega.initial_index() == ordinal(0)
    assert two.ordinal_sum(three) == ordinals(5)
    assert two.ordinal_product(three) == ordinals(6)
    assert two.ordinal_power(three) == ordinals(8)


def test_ordinal_morphisms_are_unique_exactly_along_order() -> None:
    ordinals = Ordinals()
    two = ordinals(2)
    three = ordinals(3)
    arrow = two.Mor(three)
    identity = two.Mor(two)

    assert arrow.domain() is two
    assert arrow.codomain() is three
    assert not arrow.is_identity()
    assert identity.is_identity()
