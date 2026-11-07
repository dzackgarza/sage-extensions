r"""Integral preimages in Z/2 plus Z retain the free-coordinate divisibility."""

from sage_extensions.all import *


def test_preimages_in_z_mod_two_plus_z_have_even_free_coordinate():
    r"""The image of (a,b) -> (a mod 2,2b) consists of the even free fibres."""
    source = ZZ**2
    e, f = tuple(source.module_generators())
    quotient = source.subobject_on((2 * e,)).inclusion().cokernel()
    projection = quotient.cokernel_projection()
    morphism = source.Mor(quotient)({0: projection(e), 1: projection(2 * f)})

    for target in (projection(e), projection(f), projection(e + 4 * f), projection(2 * f), projection(e - f)):
        if target in (projection(f), projection(e - f)):
            assert morphism.is_in_image(target) is False
        else:
            assert morphism.is_in_image(target) is True
            assert morphism(morphism.preimage(target)) == target
