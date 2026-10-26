r"""Positive-cone components and the hyperbolic line of the Lorentz plane ``<2> + <-2>``."""

from sage_extensions.all import *


def test_positive_cone_component_through_a_timelike_vector_separates_the_two_sheets() -> None:
    r"""The timelike vectors ``v^2 > 0`` form two components exchanged by ``-1``:
    the component through ``a`` contains ``a`` but not ``-a``, no spacelike
    vector lies in either, and the opposite component contains ``-a``.
    """
    lattice = Lattices(ZZ)([[2, 0], [0, -2]])
    timelike, spacelike = lattice.module_generators()
    component = lattice.positive_cone_component(timelike)

    assert component.contains(timelike)
    assert component.contains(2 * timelike + spacelike)
    assert not component.contains(-timelike)
    assert not component.contains(spacelike)
    assert component.opposite().contains(-timelike)


def test_hyperbolic_space_identifies_positive_multiples_of_a_timelike_vector() -> None:
    r"""Points of hyperbolic space are rays in the positive cone, so ``a`` and
    ``3a`` are one point while ``a`` and ``2a + b`` are distinct.
    """
    lattice = Lattices(ZZ)([[2, 0], [0, -2]])
    timelike, spacelike = lattice.module_generators()
    space = lattice.hyperbolic_space(timelike)

    assert space.rational_point(timelike) == space.rational_point(3 * timelike)
    assert space.rational_point(timelike) != space.rational_point(2 * timelike + spacelike)


def test_projectivized_isotropic_cone_is_the_whole_hyperbolic_line_with_two_ideal_ends() -> None:
    r"""The cone spanned by ``a^* - b^*`` and ``a^* + b^*`` projectivizes to the
    whole hyperbolic line: no ordinary vertex, two ideal vertices (the isotropic
    directions), and hence not compact.
    """
    lattice = Lattices(ZZ)([[2, 0], [0, -2]])
    timelike, _spacelike = lattice.module_generators()
    first, second = lattice.dual_module().module_generators()
    cone = lattice.rational_polyhedral_cone((first - second, first + second), complete=True)

    polyhedron = lattice.hyperbolic_space(timelike).projectivize_cone(cone)
    assert polyhedron.ordinary_vertices().cardinality() == 0
    assert polyhedron.ideal_vertices().cardinality() == 2
    assert not polyhedron.is_compact()
