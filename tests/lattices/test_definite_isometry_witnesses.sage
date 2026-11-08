r"""Integral definite isometry witnesses in canonical root and standard lattices.

Replacing the first basis vector by itself plus twice the second has
unimodular transition matrix. It therefore gives an integral isometry in
both directions, for either sign of the form.
"""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("name, sign", (("A2", 1), ("D4", -1), ("E8", -1), ("I8", -1)), ids=("A2", "negative_D4", "negative_E8", "negative_I8"))
def test_definite_lattice_isometry_witnesses_across_integral_basis_changes(name, sign):
    source = (Lattices(ZZ)(ZZ ** 8) if name == "I8" else Lattices(ZZ)(name)).twist(sign)
    basis = tuple(source.module_generators())
    changed = (basis[0] + 2 * basis[1], *basis[1:])
    target = Lattices(ZZ)(tuple(tuple(source.b(x, y) for y in changed) for x in changed))
    witness = source.Isom(target).an_element()
    assert witness.domain() is source and witness.codomain() is target
    assert abs(witness.determinant()) == ZZ.one()
    assert all(target.b(witness(x), witness(y)) == source.b(x, y) for x in basis for y in basis)
    assert all((~witness)(witness(point)) == point for point in basis)
    assert all(witness((~witness)(point)) == point for point in target.module_generators())


def test_even_binary_forms_of_determinant_twenty_three_with_different_minima_are_not_isometric():
    r"""The forms 2x²+2xy+12y² and 4x²+2xy+6y² have minima two and four.

    They have the same genus: at 23 the units 2 and 4 are squares;
    at 2 both are even unimodular binary forms of determinant 7 modulo 8.
    At the other primes they are unimodular with the same determinant.
    Completing the square in x bounds every value with nonzero y above
    those respective minima. The values at (1,0) attain the minima.
    """
    first = Lattices(ZZ)(((2, 1), (1, 12)))
    second = Lattices(ZZ)(((4, 1), (1, 6)))
    assert first.genus() == second.genus()
    assert first.Isom(second).is_empty()
    assert second.Isom(first).is_empty()

