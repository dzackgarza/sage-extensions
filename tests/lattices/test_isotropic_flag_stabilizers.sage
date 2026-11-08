r"""A null flag stabilizer fixes each term; pointwise stabilization fixes its top.

In 3U a Levi shear preserves <e> < <e,u> but moves u. Exchanging
the first two hyperbolic pairs preserves the top and moves the line.
Exchanging the third pair fixes the top pointwise and has determinant -1.
"""

from sage_extensions.all import *


def test_null_flag_stabilizers_retain_the_terms_and_the_requested_subgroup():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic + hyperbolic
    e, f, u, v, w, z = tuple(ambient.module_generators())
    labels = tuple(ambient.module_generating_set())
    flag = ambient.isotropic_flag(e, u)
    shear = ambient.Aut()(dict(zip(labels, (e, f-v, u+e, v, w, z), strict=True)))
    exchange = ambient.Aut()(dict(zip(labels, (u, v, e, f, w, z), strict=True)))
    reverse_complement = ambient.Aut()(dict(zip(labels, (e, f, u, v, z, w), strict=True)))
    setwise = ambient.O().stabilizer(flag)
    pointwise = ambient.O().stabilizer(flag, action="pointwise")
    assert shear in setwise
    assert shear not in pointwise
    assert exchange not in setwise
    assert reverse_complement in pointwise
    special = ambient.SO().stabilizer(flag)
    assert shear in special
    assert reverse_complement not in special
    special_pointwise = ambient.SO().stabilizer(flag, action="pointwise")
    assert reverse_complement not in special_pointwise
    assert ambient.O().one() in special_pointwise
    for stabilizer in (setwise, pointwise, special, special_pointwise):
        assert ambient.O().one() in stabilizer
