r"""Archive reconciliation for lattice subobject arithmetic."""

from sage_extensions.all import *


def test_lattice_subobject_sum_and_intersection_are_actual_embedded_operations() -> None:
    square = Lattices(ZZ)(ZZ**2)
    e1, e2 = square.module_generators()
    even = square.subobject_on((2 * e1, 2 * e2))
    triple = square.subobject_on((3 * e1, 3 * e2))

    intersection = even.intersection(triple)
    generated_sum = even.sum(triple)

    # 2 Z^2 cap 3 Z^2 = 6 Z^2, of index 6^2.
    assert intersection.inclusion().codomain() is square
    assert intersection.index() == 36

    # Bezout gives 2 Z^2 + 3 Z^2 = Z^2.
    assert generated_sum.inclusion().codomain() is square
    assert generated_sum.index() == 1
