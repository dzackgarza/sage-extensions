r"""The inverse image of {Id,-Id} modulo three at a null line in 2U.

Quotient negation lifts by global negation, which reverses the null line.
A pointwise lift cannot be -Id modulo three. Its quotient is -Id, so it
cannot be Id modulo three either. The pointwise unipotent kernel has
translation parameters 3 Hom(U,ZZ), of index nine in Hom(U,ZZ).
"""

from sage_extensions.all import *


def _mod_three_representation(ambient):
    scalar_change = ambient.orthogonal_group_base_change(PrimeFields()(3).quotient_map())
    changed = scalar_change.codomain().domain()
    general_linear = changed.general_linear_group()
    assert general_linear.is_finite() is True

    def reduce(isometry):
        reduced = scalar_change(isometry)
        return general_linear({label: reduced(changed.module_generator(label)) for label in changed.module_generating_set()})

    representation = ambient.O().Mor(general_linear)(reduce)
    image = representation.image()
    assert image.cardinality().is_finite() is True
    return representation.image_factorization()[0]


def test_congruence_levi_lifts_and_kernel_retain_the_modulus_three_condition():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic
    e, f, u, v = tuple(ambient.module_generators())
    labels = tuple(ambient.module_generating_set())
    reduction = ambient.primitive_isotropic_subobject(e).isotropic_reduction()
    negative = ambient.Aut()(dict(zip(labels, (e, f, -u, -v), strict=True)))
    global_negative = ambient.Aut()({label: -ambient.module_generator(label) for label in labels})
    representation = _mod_three_representation(ambient)
    target = representation.codomain().subgroup((representation(global_negative),))
    subgroup = representation.preimage_subgroup(target)
    assert negative not in subgroup and global_negative in subgroup
    minus = reduction.levi_action()(negative)
    lift = reduction.levi_lift(minus, subgroup=subgroup)
    assert lift in subgroup and lift(e) == -e
    assert reduction.levi_action()(lift) == minus
    assert all((~lift)(lift(point)) == point for point in (e, f, u, v))
    assert reduction.pointwise_levi_lift(minus, subgroup=subgroup) is None
    parameters = ZZ.free_module(2)
    parameter_labels = tuple(parameters.module_generating_set())
    inclusion = reduction.isotropic_embedding()
    null_label = next(iter(inclusion.domain().module_generating_set()))
    shifts = []
    for generator in reduction.unipotent_kernel(subgroup=subgroup).group_generators():
        assert generator in subgroup and generator(e) == e
        assert reduction.levi_action()(generator) == reduction.O().one()
        values = tuple(inclusion.lift(generator(point)-point).to_vector()(null_label) for point in (u, v))
        assert all(value % 3 == 0 for value in values)
        shifts.append(parameters.linear_combination(dict(zip(parameter_labels, values, strict=True))))
    assert parameters.subobject_on(shifts).inclusion().cokernel().cardinality() == cardinal(9)
