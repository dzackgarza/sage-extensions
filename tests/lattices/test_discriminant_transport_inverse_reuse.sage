r"""Conjugating an invariant discriminant action reuses its stored inverse pair.

Regression for the transport named in ``research#621``: converting one
invariant discriminant automorphism to a coinvariant one must keep the exact
forward/inverse module maps instead of asking the generic finite
presented-module solver to rediscover an inverse, which rebuilds a finite
presentation per call.

The specimen is ``U + U`` with the involution exchanging the summands and
``h = e + u + f + v``: both discriminant forms are glued in full, so the
conjugation ``gamma g gamma^-1`` is the whole computation.
"""

from sage_extensions.all import Lattices, ZZ


def _exchange_extension():
    lattice = Lattices(ZZ)([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    e, f, u, v = tuple(lattice.module_generators().values())
    involution = lattice.O()({0: u, 1: v, 2: e, 3: f})
    return involution.polarized(e + u + f + v).primitive_extension()


def test_coinvariant_discriminant_transport_preserves_inverse_and_glue() -> None:
    extension = _exchange_extension()
    invariant_group = extension.invariant.discriminant_image()
    coinvariant_form = extension.orthogonal_complement.discriminant_group()
    module_mor = coinvariant_form.module_category().Mor(coinvariant_form, coinvariant_form)

    assert invariant_group.group_generators()
    for generator in invariant_group.group_generators():
        transported = extension._coinvariant_discriminant_from_invariant(generator)
        transported_inverse = extension._coinvariant_discriminant_from_invariant(generator.inverse())

        assert transported.parent() is coinvariant_form.O()
        assert transported_inverse.parent() is coinvariant_form.O()
        # A form isometry whose value map is the identity is its module
        # component: the formed-module constructor returns that exact arrow,
        # so the stored forward/inverse pair keeps the module Mor parent.
        assert transported.forward().parent() is module_mor
        assert transported.inverse_morphism().parent() is module_mor
        assert transported_inverse.forward().parent() is module_mor
        assert transported_inverse.inverse_morphism().parent() is module_mor

        # The inverse of the transported action is the transport of the
        # inverse action, and it reuses the stored pair by object identity
        # rather than solving a new one.
        inverse_from_pair = transported.inverse()
        assert inverse_from_pair == transported_inverse
        assert inverse_from_pair.forward() is transported.inverse_morphism()
        assert inverse_from_pair.inverse_morphism() is transported.forward()
        for element in coinvariant_form.module_generators():
            assert transported_inverse(transported(element)) == element
            assert transported(transported_inverse(element)) == element


def test_the_glue_data_and_its_inclusion_inverses_are_built_once() -> None:
    r"""The per-automorphism cost must not rebuild the fixed glue data."""
    extension = _exchange_extension()
    glue_data = extension._full_discriminant_glue_data()
    inverse_maps = extension._coinvariant_glue_inverse_maps()

    assert extension._full_discriminant_glue_data() is glue_data
    assert extension._coinvariant_glue_inverse_maps() is inverse_maps
    assert inverse_maps[:5] == glue_data

    glue, invariant_form, coinvariant_form, glue_source, glue_target, source_inclusion, target_inclusion, source_inverse, target_inverse, glue_inverse = inverse_maps
    for label in invariant_form.module_generating_set():
        element = invariant_form.module_generator(label)
        assert source_inclusion(source_inverse(element)) == element
    for label in target_inclusion.codomain().module_generating_set():
        element = target_inclusion.codomain().module_generator(label)
        assert target_inclusion(target_inverse(element)) == element
