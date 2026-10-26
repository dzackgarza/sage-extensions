r"""Primitive duals of lattice vectors."""

from sage_extensions.all import *


def test_primitive_dual_retains_the_actual_dual_lattice_element() -> None:
    lattice = NamedLattices.U_2
    vector = lattice.module_generators()[0]
    dual = vector.primitive_dual()

    assert vector.div() == 2
    assert dual.parent() is lattice.dual_lattice()
    assert lattice.dual_lattice().scalar_multiple(2, dual) == lattice.correlation_morphism()(vector)
    assert lattice.discriminant_class(dual) == vector.divided_discriminant_class()
