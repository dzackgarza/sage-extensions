r"""Composition of affine maps between real affine spaces of distinct dimensions."""

from sage_extensions.all import *


def test_composition_of_affine_maps_between_different_models() -> None:
    r"""If f(x)=(2x+1,3x-2) and g(y,z)=(y+z+3,2y-z+4,z-1),
    then g(f(x))=(5x+2,x+8,3x-3), with linear part x |-> (5x,x,3x).
    """
    source = RR.free_module(1)
    middle = RR.free_module(2)
    target = RR.free_module(3)
    A = RealVectorSpaces(1).affinization()(source)
    B = RealVectorSpaces(2).affinization()(middle)
    C = RealVectorSpaces(3).affinization()(target)

    linear_f = source.hom([middle((2, 3))], codomain=middle)
    linear_g = middle.hom([target((1, 2, 0)), target((1, -1, 1))], codomain=target)
    affine = RealAffineSpaces()
    f = affine.Mor(A, B)(
        linear_f,
        Sets().Mor(source, middle)(lambda x: linear_f(x) + middle((1, -2))),
    )
    g = affine.Mor(B, C)(
        linear_g,
        Sets().Mor(middle, target)(lambda y: linear_g(y) + target((3, 4, -1))),
    )

    composite = g * f
    assert composite.domain() is A
    assert composite.codomain() is C
    assert composite.linear_part().domain() is source
    assert composite.linear_part().codomain() is target
    assert composite.point_map().domain() is source
    assert composite.point_map().codomain() is target
    assert composite(source.zero()) == target((2, 8, -3))
    assert composite(source((2,))) == target((12, 10, 3))
    assert composite.linear_part()(source((2,))) == target((10, 2, 6))


def test_real_linear_endomorphism_composition_uses_owned_scalars() -> None:
    r"""For s(x,y)=(x+y,y) and t(x,y)=(2x,y-x), t(s(x,y))=(2x+2y,-x)."""
    plane = RR.free_module(2)
    s = plane.hom([plane((1, 0)), plane((1, 1))], codomain=plane)
    t = plane.hom([plane((2, -1)), plane((0, 1))], codomain=plane)

    composite = t * s
    assert composite.domain() is plane
    assert composite.codomain() is plane
    assert composite(plane((3, 4))) == plane((14, -3))
