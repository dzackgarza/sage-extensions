r"""Finite cokernel construction retains its arrow and an actual free presentation."""


from sage_extensions.all import *


def test_infinite_numerator_module_can_have_finite_zero_localization():
    ring = ZZ.polynomial_ring(("x",))
    x = ring.algebra_generator("x")
    free = ring.free_module(1)
    numerator = free.Mor(free)({0: x * free.module_generator(0)}).cokernel()
    localized = ring.localization(x).localize_module(numerator)
    assert localized in AdditiveGroups().AdditiveCommutative()
    assert localized.is_zero() is True
    assert localized.is_finite() is True
