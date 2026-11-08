r"""The null-line quotient image of SO(2U) is SO(U), with exact lifts.

On the rational filtration I < I-perp < L a parabolic isometry has
determinant det(A) det(g_K) det(A^-T) = det(g_K). Thus exchanging the
quotient hyperbolic basis has no SO lift, while quotient negation does.
"""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("pointwise", (False, True), ids=("setwise", "pointwise"))
def test_special_orthogonal_null_line_has_its_proper_quotient_image(pointwise):
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic
    e, f, u, v = tuple(ambient.module_generators())
    labels = tuple(ambient.module_generating_set())
    space = ambient.primitive_isotropic_subobject(e)
    reduction = space.isotropic_reduction()
    full = reduction.levi_action()
    negative = ambient.Aut()(dict(zip(labels, (e, f, -u, -v), strict=True)))
    exchange = ambient.Aut()(dict(zip(labels, (e, f, v, u), strict=True)))
    minus = full(negative)
    swapped = full(exchange)
    subgroup = ambient.SO()
    action = reduction.pointwise_levi_action(subgroup=subgroup) if pointwise else reduction.levi_action(subgroup=subgroup)
    image = reduction.pointwise_levi_image(subgroup=subgroup) if pointwise else reduction.levi_image(subgroup=subgroup)
    assert minus in image
    assert swapped not in image
    lift = reduction.pointwise_levi_lift(minus, subgroup=subgroup) if pointwise else reduction.levi_lift(minus, subgroup=subgroup)
    assert lift in subgroup and lift in space.parabolic_subgroup()
    assert full(lift) == minus
    if pointwise:
        assert lift(e) == e
    assert all((~lift)(lift(point)) == point for point in (e, f, u, v))
    assert image.cardinality() == cardinal(2)
    assert all(generator in image for generator in image.group_generators())
    if not pointwise:
        assert any(generator == minus for generator in reduction.levi_image_generators(subgroup=subgroup))


def test_spinor_subgroup_lift_adjusts_the_null_action_and_preserves_the_quotient():
    r"""The real spinor sign of -Id_U is negative; two such factors cancel.

    Fixing the line leaves only Eichler translations in the quotient
    kernel, all with trivial spinor norm. A pointwise lift cannot cancel
    the negative quotient sign, while reversing the null line can.
    """
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic
    e, f, u, v = tuple(ambient.module_generators())
    labels = tuple(ambient.module_generating_set())
    reduction = ambient.primitive_isotropic_subobject(e).isotropic_reduction()
    negative = ambient.Aut()(dict(zip(labels, (e, f, -u, -v), strict=True)))
    global_negative = ambient.Aut()({label: -ambient.module_generator(label) for label in labels})
    subgroup = ambient.O_plus()
    assert negative not in subgroup and global_negative in subgroup
    minus = reduction.levi_action()(negative)
    action = reduction.levi_action(subgroup=subgroup)
    lift = action.lift(minus)
    assert lift in subgroup
    assert lift(e) == -e
    assert reduction.levi_action()(lift) == minus
    assert all((~lift)(lift(point)) == point for point in (e, f, u, v))
    assert minus not in reduction.pointwise_levi_action(subgroup=subgroup).image()
    parameters = ZZ.free_module(2)
    parameter_labels = tuple(parameters.module_generating_set())
    inclusion = reduction.isotropic_embedding()
    null_label = next(iter(inclusion.domain().module_generating_set()))
    shifts = []
    for generator in reduction.unipotent_kernel(subgroup=subgroup).group_generators():
        assert generator in subgroup and generator(e) == e
        assert reduction.levi_action()(generator) == reduction.O().one()
        values = tuple(inclusion.lift(generator(point)-point).to_vector()(null_label) for point in (u, v))
        shifts.append(parameters.linear_combination(dict(zip(parameter_labels, values, strict=True))))
    assert parameters.subobject_on(shifts).inclusion().cokernel().cardinality() == cardinal(1)
