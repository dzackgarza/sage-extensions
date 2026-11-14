r"""Integral indefinite isometry witnesses for lattices given by Gram rows.

``U + <2>`` is even, indefinite of signature (2, 1) and rank three. Replacing
the first basis vector by itself plus twice the second has unimodular
transition matrix, so the Gram rows in the new basis give an isometric
lattice. Neither lattice is constructed as a direct sum.
"""

from sage_extensions.all import *


def test_indefinite_gram_row_lattices_have_an_isometry_witness():
    source = Lattices(ZZ)(((0, 1, 0), (1, 0, 0), (0, 0, 2)))
    basis = tuple(source.module_generators())
    changed = (basis[0] + 2 * basis[1], *basis[1:])
    target = Lattices(ZZ)(tuple(tuple(source.b(x, y) for y in changed) for x in changed))
    witness = source.Isom(target).an_element()
    assert witness.domain() is source and witness.codomain() is target
    assert abs(witness.determinant()) == ZZ.one()
    assert all(target.b(witness(x), witness(y)) == source.b(x, y) for x in basis for y in basis)
