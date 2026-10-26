r"""The polarization of the toric surface of `2\Delta = \operatorname{conv}\{(0,0),(2,0),(0,2)\}`.

Source: Cox, Little, Schenck, *Toric Varieties*, Prop. 4.3.3 and Thm. 6.2.1: the
toric variety of `2\Delta` is `\mathbb{P}^2` polarized by `\mathcal{O}(2)`, the
polytope of the polarizing divisor is `2\Delta` again, and its six lattice points
are the monomials of degree 2.  The sum of all six,
`x^2 + y^2 + z^2 + xy + xz + yz`, has Gram determinant `1/2 \ne 0`, so its zero
locus is a smooth conic.
"""

from sage_extensions.all import *


def test_the_polarizing_divisor_of_twice_the_triangle_recovers_it_and_cuts_a_smooth_conic() -> None:
    lattice = ZZ.free_module(2)
    polygon = ConvexPolytopes(lattice)(((0, 0), (2, 0), (0, 2)))
    surface = polygon.toric_variety(QQ)
    divisor = surface.polarizing_divisor()
    sections = surface.divisor_section_space(divisor)
    section = sections.linear_combination(
        {label: QQ.one() for label in sections.module_generating_set()}
    )
    conic = surface.zero_subscheme_of_divisor_section(divisor, section)

    assert surface.divisor_polytope(divisor) == polygon
    assert sections.dimension() == 6
    assert conic.relative_dimension() == 1
    assert conic.is_smooth()
    assert conic.genus() == 0
