r"""An integral lattice scaled by a large integer is still decided across basis changes.

Scaling every pairing by the positive integer ``2**61`` multiplies the Gram
matrix by ``2**61`` and leaves the isometry relation alone: a unimodular
change of basis carries one form to the other exactly as it does for the
unscaled root lattice, and the transition matrix below is one (it replaces
the first basis vector by itself plus the second, so its determinant is one).

The Gram matrices are the datum of these lattices, and both of them are Gram
matrices of A_3 scaled by ``2**61``: the second in the basis ``(b1 + b2, b2,
b3)``.  A lattice whose minimal vector has that norm is an ordinary integral
lattice, so the isometry has to be decided here, and the witness it is decided
with has to be an isometry in both directions.
"""

from sage_extensions.all import *


def test_an_integral_lattice_scaled_by_a_large_integer_keeps_its_isometries():
    scale = ZZ(2) ** 61
    root = ((2, -1, 0), (-1, 2, -1), (0, -1, 2))
    gram = tuple(tuple(scale * ZZ(entry) for entry in row) for row in root)
    source = Lattices(ZZ)(gram)
    basis = tuple(source.module_generators())
    changed = (basis[0] + basis[1], *basis[1:])
    target = Lattices(ZZ)(tuple(tuple(source.b(x, y) for y in changed) for x in changed))
    witness = source.Isom(target).an_element()
    assert witness.domain() is source and witness.codomain() is target
    assert abs(witness.determinant()) == ZZ.one()
    assert all(target.b(witness(x), witness(y)) == source.b(x, y) for x in basis for y in basis)
    assert all((~witness)(witness(point)) == point for point in basis)
    assert all(witness((~witness)(point)) == point for point in target.module_generators())
