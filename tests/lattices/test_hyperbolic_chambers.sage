r"""Rational polyhedral cones and reflection chambers of small hyperbolic lattices."""

from sage_extensions.all import *


def test_the_isotropic_cone_of_the_lorentz_plane_has_two_ideal_rays() -> None:
    r"""On ``<2> + <-2>`` the covectors ``a^* - b^*`` and ``a^* + b^*`` span the
    cone over the two isotropic directions: it is pointed, both its rays are
    ideal (isotropic), none is timelike, and the timelike vector ``a`` lies in
    the closed positive cone it bounds.
    """
    lattice = Lattices(ZZ)([[2, 0], [0, -2]])
    first, second = lattice.dual_module().module_generators()
    timelike, _spacelike = lattice.module_generators()

    future = lattice.rational_polyhedral_cone((first - second, first + second))
    assert future.is_pointed()
    assert future.lies_in_closed_positive_cone(timelike)
    assert future.ideal_rays().cardinality() == 2
    assert future.timelike_rays().cardinality() == 0


def test_hilbert_basis_of_a_nonunimodular_plane_cone_exceeds_its_rays() -> None:
    r"""The cone in ``ZZ^2`` spanned by ``(1,0)`` and ``(1,2)`` has index ``2``,
    so its Hilbert basis is ``(1,0), (1,1), (1,2)``: three elements against two
    primitive rays and two facets.  Derived by hand from the fundamental
    parallelogram, whose only interior lattice point is ``(1,1)``.
    """
    lattice = Lattices(ZZ)([[1, 0], [0, 1]])
    first, second = lattice.dual_module().module_generators()

    cone = lattice.rational_polyhedral_cone((first, first + 2 * second))
    assert cone.is_pointed()
    assert cone.primitive_rays().cardinality() == 2
    assert cone.facet_covectors().cardinality() == 2
    assert cone.hilbert_basis().cardinality() == 3
    assert first + second in cone.hilbert_basis()


def test_lorentz_plane_has_one_reflective_wall_and_orthogonal_group_of_order_four() -> None:
    r"""On ``<2> + <-2>`` (basis ``a, b``) the only roots are ``+-b``, since
    ``x^2 - y^2 = -1`` forces ``x = 0``; and ``x^2 - y^2 = 1`` forces ``y = 0``,
    so ``O(L) = {+-1} x {+-1}`` has order ``4`` and the Weyl group is
    ``<s_b>`` of order ``2``.  The fundamental chamber has the single wall
    ``b^perp``.  Derived by hand.
    """
    lattice = Lattices(ZZ)([[2, 0], [0, -2]])
    a, b = lattice.module_generators()

    assert lattice.O().cardinality() == 4
    assert lattice.weyl_group().cardinality() == 2
    walls = lattice.fundamental_chamber().wall_roots()
    assert walls.cardinality() == 1
    for root in walls:
        assert lattice.b(root, root) == -2
        assert lattice.b(root, a) == 0
