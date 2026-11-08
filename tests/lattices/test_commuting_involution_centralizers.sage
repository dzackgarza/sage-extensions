r"""Centralizers of commuting involutions on U1+U2.

f1 is +1 on U1 and -1 on U2; f2 swaps e,f on U1 and fixes U2. The joint
eigensublattices are Z(e+f)=<2>, Z(e-f)=<-2> and U2. The glue of U1 has order
two with trivial action of the signs, so the centralizer has order 2*2*4=16.
"""

import pytest

from sage_extensions.all import *


def test_two_commuting_involutions_have_centralizer_of_order_sixteen():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic
    e, f, u, v = tuple(ambient.module_generators())
    labels = tuple(ambient.module_generating_set())
    group = ambient.O()
    first = ambient.Aut()(dict(zip(labels, (e, f, -u, -v), strict=True)))
    second = ambient.Aut()(dict(zip(labels, (f, e, u, v), strict=True)))
    pieces = group.joint_eigensublattices((first, second))
    assert len(pieces) == 3
    generators = group.commuting_involutions_centralizer_generators((first, second))
    assert group.subgroup(generators).cardinality() == cardinal(16)
    assert all(element(first(x)) == first(element(x)) and element(second(x)) == second(element(x)) for element in generators for x in (e, f, u, v))


def test_eigensublattices_of_a_nonsymmetric_involution_are_eigenvectors():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic
    e, f, u, v = tuple(ambient.module_generators())
    labels = tuple(ambient.module_generating_set())
    shear = ambient.Aut()(dict(zip(labels, (e, f-v, u+e, v), strict=True)))
    swap = ambient.Aut()(dict(zip(labels, (f, e, u, v), strict=True)))
    conjugate = shear * swap * ~shear
    pieces = ambient.O().joint_eigensublattices((conjugate,))
    for (sign,), piece in pieces.items():
        inclusion = piece.inclusion()
        for point in piece.module_generators():
            assert conjugate(inclusion(point)) == sign * inclusion(point)


def test_noncommuting_involutions_are_rejected():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic
    e, f, u, v = tuple(ambient.module_generators())
    labels = tuple(ambient.module_generating_set())
    first = ambient.Aut()(dict(zip(labels, (u, v, e, f), strict=True)))
    second = ambient.Aut()(dict(zip(labels, (f, e, u, v), strict=True)))
    with pytest.raises(ValueError):
        ambient.O().joint_eigensublattices((first, second))
