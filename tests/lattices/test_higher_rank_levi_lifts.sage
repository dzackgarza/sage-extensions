r"""A split null-plane parabolic in 3U + <2> lifts O(U + <2>).

Fixing the first two hyperbolic planes and applying an integral isometry
of the last U + <2> is an integral ambient lift. The quotient transvection
(u,v,w) -> (u,v+w-u,w-2u) has infinite order and preserves the form.
"""

from sage_extensions.all import *


def test_null_plane_levi_section_lifts_a_quotient_transvection():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic + hyperbolic + Lattices(ZZ)([[2]])
    e, f, a, b, u, v, w = tuple(ambient.module_generators())
    labels = tuple(ambient.module_generating_set())
    isotropic = ambient.primitive_isotropic_subobject(e, a)
    reduction = isotropic.isotropic_reduction()
    levi = reduction.levi_action()
    known = ambient.Aut()(dict(zip(labels, (e, f, a, b, u, v+w-u, w-2*u), strict=True)))
    quotient_map = levi(known)
    assert quotient_map != levi.codomain().one()
    assert known(e) == e and known(a) == a
    lift = levi.lift(quotient_map)
    assert levi(lift) == quotient_map
    assert lift in isotropic.parabolic_subgroup()
    for source in (e, a):
        assert isotropic.inclusion().is_in_image(lift(source))
        assert isotropic.inclusion().is_in_image((~lift)(source))
    assert all((~lift)(lift(point)) == point for point in ambient.module_generators())
    assert all(ambient.b(lift(x), lift(y)) == ambient.b(x, y) for x in ambient.module_generators() for y in ambient.module_generators())
