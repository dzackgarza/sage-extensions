r"""Least integral orbit spans in a rational plane.

For s(e)=2f and s(f)=e/2, s^2=1. The span of e,f and their images is
Z(e/2)+Zf, which is stable. This proves the least-span assertion independently
of the computation and distinguishes it from a larger supplied bound.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_the_least_stable_span_retains_its_inclusion_and_seed_factorization():
    plane = Lattices(QQ)("U", module_generators=("east", "north"))
    e, f = tuple(plane.module_generators())
    labels = tuple(plane.module_generating_set())
    half = QQ.one() / 2
    symmetry = plane.O()({labels[0]: 2 * f, labels[1]: half * e})
    group = plane.O().subgroup((symmetry,))
    space = Modules(QQ).restriction_of_scalars(ZZ.fraction_field_map())(plane)
    seed = space.subobject_on((space(e), space(f)))
    bound = space.subobject_on((space(half * half * e), space(half * f)))
    construction = IntegralStructureAction(group, seed.inclusion()).with_stable_containing_bound(
        bound.inclusion(), check=True,
    ).invariant_module_construction()
    inclusion = construction.inclusion()
    expected = space.subobject_on((space(half * e), space(f)))

    assert inclusion.codomain() is space
    assert inclusion.domain().base_ring() is ZZ
    assert all(expected.inclusion().is_in_image(inclusion(point)) for point in inclusion.domain().module_generators())
    assert all(inclusion.is_in_image(expected.inclusion()(point)) for point in expected.module_generators())
    assert not inclusion.is_in_image(space(half * half * e))
    assert not inclusion.is_in_image(space(half * f))
    factor = construction.seed_factorization()
    for point in seed.module_generators():
        assert inclusion(factor(point)) == seed.inclusion()(point)
    for point in inclusion.domain().module_generators():
        assert inclusion.is_in_image(space(symmetry(inclusion(point).underlying_element())))


def test_a_containing_bound_can_be_nonstable_while_containing_the_whole_orbit_span():
    r"""Swapping coordinates closes 2Z^2 inside Ze+2Zf, although that bound is not stable."""
    plane = Lattices(QQ)("U")
    e, f = tuple(plane.module_generators())
    labels = tuple(plane.module_generating_set())
    symmetry = plane.O()({labels[0]: f, labels[1]: e})
    group = plane.O().subgroup((symmetry,))
    space = Modules(QQ).restriction_of_scalars(ZZ.fraction_field_map())(plane)
    seed = space.subobject_on((space(2 * e), space(2 * f)))
    bound = space.subobject_on((space(e), space(2 * f)))
    action = IntegralStructureAction(group, seed.inclusion()).ambient_action_functor()
    construction = GObjects(group, Modules(ZZ)).orbit_generated_submodule(
        action, seed.inclusion(), containing=bound.inclusion(),
    )
    inclusion = construction.inclusion()

    assert not bound.inclusion().is_in_image(space(f))
    assert all(seed.inclusion().is_in_image(inclusion(point)) for point in inclusion.domain().module_generators())
    assert all(inclusion.is_in_image(seed.inclusion()(point)) for point in seed.module_generators())
    assert not inclusion.is_in_image(space(e))
    assert not inclusion.is_in_image(space(f))


def test_orbit_images_outside_the_supplied_bound_are_refused():
    r"""The full integral plane does not contain the orbit of f under s(f)=e/2."""
    plane = Lattices(QQ)("U")
    e, f = tuple(plane.module_generators())
    labels = tuple(plane.module_generating_set())
    symmetry = plane.O()({labels[0]: 2 * f, labels[1]: (QQ.one() / 2) * e})
    group = plane.O().subgroup((symmetry,))
    space = Modules(QQ).restriction_of_scalars(ZZ.fraction_field_map())(plane)
    seed = space.subobject_on((space(e), space(f)))
    action = IntegralStructureAction(group, seed.inclusion()).ambient_action_functor()

    with pytest.raises(ValueError):
        GObjects(group, Modules(ZZ)).orbit_generated_submodule(
            action, seed.inclusion(), containing=seed.inclusion(),
        )
