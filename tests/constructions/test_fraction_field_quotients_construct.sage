r"""Fraction-field quotients are the divisible modules ``K / a``.

For ``K=QQ`` and ``a=6ZZ``, the class of ``1/3`` has additive order eighteen:
``18/3=6`` is the first multiple lying in ``6ZZ``.  The cyclic subgroup it
generates therefore has order eighteen even though ``QQ/6ZZ`` itself is
countably infinite.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _rationals_mod_six():
    return FractionFieldQuotients(ZZ)(6)


def test_fraction_field_quotient_retains_ring_field_modulus_and_projection() -> None:
    quotient = _rationals_mod_six()
    projection = quotient.projection_from_fraction_field()

    assert quotient in FractionFieldQuotients(ZZ)
    assert quotient in Modules(ZZ)
    assert quotient.base_ring() is ZZ
    assert quotient.fraction_field() is QQ
    assert quotient.modulus() == ZZ(6)
    assert quotient.cardinality() == aleph0
    assert projection.domain() is QQ
    assert projection.codomain() is quotient
    assert projection(QQ(6)) == quotient.zero()
    assert quotient.an_element() in quotient


def test_class_of_one_third_has_order_eighteen_and_selected_lift_one_third() -> None:
    quotient = _rationals_mod_six()
    element = quotient(QQ(1) / 3)

    assert isinstance(element, quotient.ElementType)
    assert element.additive_order() == 18
    assert quotient.lift(element) == QQ(1) / 3
    assert element.lift() == QQ(1) / 3


def test_cyclic_subobject_generated_by_one_third_has_order_eighteen() -> None:
    quotient = _rationals_mod_six()
    element = quotient(QQ(1) / 3)
    cyclic = quotient.subobject_on((element,))

    assert cyclic.cardinality() == cardinal(18)
    assert cyclic.inclusion()(cyclic.module_generator(0)) == element


def test_divisibility_chain_is_cofinal_by_successive_divisibility() -> None:
    quotient = _rationals_mod_six()
    first = quotient.divisibility_chain(0)
    second = quotient.divisibility_chain(1)

    assert first in ZZ
    assert second in ZZ
    assert first != 0
    assert second % first == 0
