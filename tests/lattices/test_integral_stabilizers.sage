r"""``G_L = {g in G : g(L) = L}`` for a lattice inside a rational space.

A lattice in a ``QQ``-space ``V`` is a ``ZZ``-submodule of the restriction of
scalars of ``V``, and the integral stabilizer of a rational group ``G`` is cut
out of ``G`` by ``g(L) = L``.  The specimens live in the hyperbolic plane over
``QQ``, where ``diag(t, 1/t)`` is an isometry for every nonzero ``t``: on the
isotropic line ``ZZ e_0`` that isometry gives ``g(L) < L``, which separates the
equality from the containment.
"""

from sage_extensions.all import *


def _rational_hyperbolic_plane_and_its_underlying_ZZ_module():
    plane = Lattices(QQ)("U")
    restriction = Modules(QQ).restriction_of_scalars(ZZ.Mor(QQ)(lambda n: QQ(n)))
    return plane, restriction(plane)


def test_diag_two_half_maps_an_isotropic_line_properly_into_itself_and_leaves_its_stabilizer() -> None:
    r"""``diag(2, 1/2)`` carries ``ZZ e_0`` onto ``2 ZZ e_0 < ZZ e_0``; ``-1`` carries it onto itself."""
    plane, space = _rational_hyperbolic_plane_and_its_underlying_ZZ_module()
    e0, e1 = plane.module_generators()
    line = space.submodule([space(e0)])
    orthogonal_group = plane.O()
    scaling = orthogonal_group({e0: 2 * e0, e1: e1 / 2})
    negation = orthogonal_group({e0: -e0, e1: -e1})

    stabilizer = IntegralStructureAction(orthogonal_group, line).stabilizer()

    assert space(scaling(e0)) in line
    assert scaling not in stabilizer
    assert negation in stabilizer


def test_the_swap_stabilizes_the_standard_lattice_but_not_a_commensurable_one() -> None:
    r"""The swap ``e_0 <-> e_1`` preserves ``ZZ e_0 + ZZ e_1`` but sends ``e_1/2`` out of ``ZZ e_0 + ZZ e_1/2``."""
    plane, space = _rational_hyperbolic_plane_and_its_underlying_ZZ_module()
    e0, e1 = plane.module_generators()
    standard = space.submodule([space(e0), space(e1)])
    finer = space.submodule([space(e0), space(e1 / 2)])
    orthogonal_group = plane.O()
    swap = orthogonal_group({e0: e1, e1: e0})

    assert swap in IntegralStructureAction(orthogonal_group, standard).stabilizer()
    assert swap not in IntegralStructureAction(orthogonal_group, finer).stabilizer()
