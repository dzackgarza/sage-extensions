r"""Finite-index free submodules modulo an explicitly supplied integral action."""
from sage_extensions.all import *


def test_full_gl_two_has_one_cyclic_index_two_submodule_orbit():
    module = Lattices(ZZ)([[0, 0], [0, 0]])
    action = module.general_linear_group().group_generators()
    orbits = module.finite_index_submodule_orbits((1, 2), action)
    assert orbits.cardinality() == cardinal(1)
    assert all(arrow.codomain() is module for arrow in orbits)
    assert all(arrow.cokernel().cardinality() == cardinal(2) for arrow in orbits)


def test_trivial_action_keeps_all_three_index_two_submodules():
    module = Lattices(ZZ)([[0, 0], [0, 0]])
    orbits = module.finite_index_submodule_orbits((1, 2), ())
    assert orbits.cardinality() == cardinal(3)
    assert all(arrow.cokernel().cardinality() == cardinal(2) for arrow in orbits)
