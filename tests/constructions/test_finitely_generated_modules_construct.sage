r"""Finitely generated modules expose fibre ranks and local generators.

The free rank-two module over ``QQ[x]`` has generic and fibre rank two at every
point.  Localizing at the origin requires two generators and has a two-dimensional
residue module.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _free_plane_over_affine_line():
    ring = QQ["x"]
    module = ring.free_module(2)
    point = ring.spectrum()(ring.ideal(ring.algebra_generator("x")))
    return ring, module, point


def test_finitely_generated_free_plane_has_constant_rank_two_fibres() -> None:
    _ring, module, point = _free_plane_over_affine_line()
    fiber = module.fiber(point)
    rank = module.rank_function()

    assert module in FinitelyGeneratedModules(module.base_ring())
    assert module.is_finitely_generated()
    assert not module.is_torsion()
    assert module.generic_rank() == 2
    assert module.fiber_dimension(point) == 2
    assert module.rank_at(point) == 2
    assert rank(point) == 2
    assert fiber.dimension() == 2
    assert len(tuple(module.local_minimal_generators(point))) == 2
    assert module.local_number_of_generators(point) == 2


def test_local_free_plane_has_two_minimal_generators_and_two_dimensional_residue() -> None:
    _ring, module, point = _free_plane_over_affine_line()
    local = module.localize_at_prime(point)

    assert local.minimal_number_of_generators() == 2
    assert local.residue_module().dimension() == 2
