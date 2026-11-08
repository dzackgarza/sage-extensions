r"""Reduction, approximate canonical form and flag invariants on a change of basis.

The form is unchanged by a change of basis and the canonical form of a
block depends only on the isometry class of the block.
"""

from sage_extensions.all import *


def _changed_basis(lattice):
    points = tuple(lattice.module_generators())
    new_basis = (points[0], points[1] + points[0] + points[2], points[2] + points[0])
    return lattice, lattice.subobject_on(new_basis).inclusion().domain(), new_basis


def test_reduction_preserves_form_and_canonical_form_is_presentation_independent():
    hyperbolic = Lattices(ZZ)("U")
    lattice = hyperbolic + Lattices(ZZ)("A1")
    _lattice, changed, _basis = _changed_basis(lattice)
    assert lattice.indefinite_reduction().reduced.is_isometric(lattice)
    first = lattice.approximate_canonical_presentation().reduced.gram_matrix()
    second = changed.approximate_canonical_presentation().reduced.gram_matrix()
    assert first == second


def test_definite_block_canonical_form_identifies_a_change_of_basis():
    a2 = Lattices(ZZ)("A2")
    x, y = tuple(a2.module_generators())
    changed = a2.subobject_on((x + y, y + (x + y) + (x + y))).inclusion().domain()
    assert changed.approximate_canonical_presentation().reduced.gram_matrix() == a2.approximate_canonical_presentation().reduced.gram_matrix()


def test_flag_invariant_is_preserved_by_an_isometry():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic
    e1, f1, e2, f2 = tuple(ambient.module_generators())
    assert IsotropicFlag(ambient, (e1,)).invariant() == IsotropicFlag(ambient, (e2,)).invariant()
