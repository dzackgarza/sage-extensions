r"""Exact relation membership for selected presentations over polynomial rings."""

from sage_extensions.all import *


def _cyclic_quotient(ring, relation):
    free = ring.free_module(1)
    generator = free.module_generator(0)
    return free.module_category().Mor(free, free)({0: relation * generator}).cokernel()


def test_multivariate_relation_membership_does_not_use_fraction_field_span() -> None:
    ring = QQ.polynomial_ring(("x", "y"))
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    module = _cyclic_quotient(ring, x)
    generator = module.module_generator(0)

    assert generator != module.zero()
    assert module.scalar_multiple(x, generator) == module.zero()
    assert module.scalar_multiple(y, generator) != module.zero()
