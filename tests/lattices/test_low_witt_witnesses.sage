r"""Changed-basis isometry witnesses at rational Witt index below two.

diag(2,2,-6,-6) has Witt index zero and U+<2,-4> has Witt index one. A
unimodular change of basis is an isometry; a form of different determinant is not.
"""

from sage_extensions.all import *
from sage_indefinite_port.indefinite.marked_lattices import RECURSION


def _changed(lattice):
    a, b, c, d = tuple(lattice.module_generators())
    return lattice.subobject_on((a + b, b, c + a, d + c)).inclusion().domain()


def _assert_witness(lattice):
    changed = _changed(lattice)
    witness = RECURSION.isometry(lattice, changed)
    assert witness is not None and witness.domain() is lattice and witness.codomain() is changed
    points = tuple(lattice.module_generators())
    assert all(changed.b(witness(x), witness(y)) == lattice.b(x, y) for x in points for y in points)


def test_witt_zero_changed_basis_witness():
    lattice = Lattices(ZZ)([[2, 0, 0, 0], [0, 2, 0, 0], [0, 0, -6, 0], [0, 0, 0, -6]])
    assert int(lattice.witt_index()) == 0
    _assert_witness(lattice)


def test_witt_one_changed_basis_witness():
    lattice = Lattices(ZZ)([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 2, 0], [0, 0, 0, -4]])
    assert int(lattice.witt_index()) == 1
    _assert_witness(lattice)


def test_different_forms_have_no_witness():
    first = Lattices(ZZ)([[2, 0, 0, 0], [0, 2, 0, 0], [0, 0, -6, 0], [0, 0, 0, -6]])
    second = Lattices(ZZ)([[2, 0, 0, 0], [0, 2, 0, 0], [0, 0, -6, 0], [0, 0, 0, -10]])
    assert RECURSION.isometry(first, second) is None


def test_fair_enumeration_starts_with_isometries_and_has_exact_membership():
    from itertools import islice

    from sage_indefinite_port.indefinite.low_witt import fair_orthogonal_group_elements

    lattice = Lattices(ZZ)([[2, 0, 0, 0], [0, 2, 0, 0], [0, 0, -6, 0], [0, 0, 0, -6]])
    points = tuple(lattice.module_generators())
    elements = tuple(islice(fair_orthogonal_group_elements(lattice), 16))
    assert len({tuple(element(point) for point in points) for element in elements}) == 16
    assert all(lattice.b(element(x), element(y)) == lattice.b(x, y) for element in elements for x in points for y in points)
