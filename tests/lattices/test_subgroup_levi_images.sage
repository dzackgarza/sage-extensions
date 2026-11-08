r"""The null-line quotient image of SO(2U) is SO(U), with exact lifts.

On the rational filtration I < I-perp < L a parabolic isometry has
determinant det(A) det(g_K) det(A^-T) = det(g_K). Thus exchanging the
quotient hyperbolic basis has no SO lift, while quotient negation does.
"""

from sage_extensions.all import *


def test_special_orthogonal_null_line_has_its_proper_quotient_image():
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
    action = reduction.levi_action(subgroup=subgroup)
    image = action.image()
    assert minus in image
    assert swapped not in image
    lift = action.lift(minus)
    assert lift in subgroup and lift in space.parabolic_subgroup()
    assert full(lift) == minus
    assert all((~lift)(lift(point)) == point for point in (e, f, u, v))
    assert image.cardinality() == cardinal(2)
    assert all(generator in image for generator in image.group_generators())
