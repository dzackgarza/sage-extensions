r"""The null-plane Levi GL action is restriction along its inclusion.

The integral shear and hyperbolic-pair exchange in 2U induce the
standard shear and exchange of the null basis. Restriction commutes
with that inclusion, products and inverses.
"""

from sage_extensions.all import *


def test_null_plane_parabolic_restriction_is_the_actual_gl_action():
    ambient = Lattices(ZZ)("U") + Lattices(ZZ)("U")
    e, f, u, v = tuple(ambient.module_generators())
    labels = tuple(ambient.module_generating_set())
    space = ambient.primitive_isotropic_subobject(e, u)
    embedding = space.inclusion()
    shear = ambient.Aut()(dict(zip(labels, (e, f-v, u+e, v), strict=True)))
    exchange = ambient.Aut()(dict(zip(labels, (u, v, e, f), strict=True)))
    action = space.isotropic_reduction().isotropic_action()
    first = action(shear)
    second = space.levi_restriction(exchange)
    assert embedding(first(embedding.lift(u))) == u+e
    assert embedding(second(embedding.lift(e))) == u
    for automorphism in (shear, exchange, shear*exchange):
        restricted = action(automorphism)
        for point in embedding.domain().module_generators():
            assert embedding(restricted(point)) == automorphism(embedding(point))
            assert (~restricted)(restricted(point)) == point
    assert action(shear*exchange) == first*second
