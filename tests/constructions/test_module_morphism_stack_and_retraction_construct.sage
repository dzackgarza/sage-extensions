r"""Module morphisms stack into biproducts and split direct-summand inclusions."""

from sage_extensions.all import *  # noqa: F401,F403


def test_two_coordinate_maps_stack_to_the_identity_of_rank_two_free_module() -> None:
    plane = ZZ.free_module(2)
    line = ZZ.free_module(1)
    first = plane.Mor(line)({0: line.module_generator(0), 1: line.zero()})
    second = plane.Mor(line)({0: line.zero(), 1: line.module_generator(0)})
    stacked = first.stack(second)

    assert stacked.domain() is plane
    assert stacked.codomain().biproduct_factor(0) is line
    assert stacked.codomain().biproduct_factor(1) is line
    assert stacked(plane.module_generator(0)) == stacked.codomain().injection(0)(line.module_generator(0))
    assert stacked(plane.module_generator(1)) == stacked.codomain().injection(1)(line.module_generator(0))


def test_first_coordinate_inclusion_retracts_by_first_projection() -> None:
    line = ZZ.free_module(1)
    plane = Modules(ZZ).biproduct((line, line))
    inclusion = plane.injection(0)
    retraction = inclusion.retraction()

    assert retraction * inclusion == line.Mor(line).identity()
    assert retraction == plane.projection(0)
