r"""A polynomial PID cokernel retains its torsion and free parts."""

from sage_extensions.all import *


def test_a_cyclic_polynomial_quotient_has_its_exact_order_and_annihilator() -> None:
    ring = PrimeFields()(5).polynomial_ring(("t",))
    t = ring.algebra_generator("t")
    free = ring.free_module(1)
    generator = free.module_generator(0)
    module = free.Mor(free)({0: free.scalar_multiple(t**2, generator)}).cokernel()

    assert module.cardinality() == cardinal(25)
    assert module.exponent() == t**2
    assert module.annihilator() == ring.ideal(t**2)


def test_a_free_summand_preserves_the_polynomial_torsion_relation() -> None:
    ring = PrimeFields()(5).polynomial_ring(("t",))
    t = ring.algebra_generator("t")
    free = ring.free_module(2)
    relations = ring.free_module(1)
    module = relations.Mor(free)({0: free.scalar_multiple(t**2, free.module_generator(0))}).cokernel()
    torsion, infinite = module.module_generator(0), module.module_generator(1)

    assert torsion != module.zero()
    assert module.scalar_multiple(t**2, torsion) == module.zero()
    assert module.scalar_multiple(t**2, infinite) != module.zero()
    assert module.annihilator() == ring.ideal(ring.zero())
