r"""The universal linear extension of a family on a free module basis.

For chosen images y_a,y_z, the extension sends e_a to y_a and e_z
to y_z and sends r e_a + s e_z to r y_a + s y_z. This law uses
left coefficients in their given order over a noncommutative ring.
The target framing is enumerated in the reverse label order.
"""

from sage_extensions.all import *

import pytest


@pytest.mark.parametrize("kind", ("rationals", "polynomials", "matrix_ring"))
def test_the_linear_extension_has_its_given_images_and_left_coefficient_law(kind):
    if kind == "rationals":
        ring = QQ
        left, right = ring(2), ring(3)
    elif kind == "polynomials":
        ring = QQ["t"]
        left = ring.algebra_generator("t")
        right = left + ring.one()
    else:
        ring = QQ.matrix_space(2)
        left, right = ring.matrix_unit(0, 1), ring.matrix_unit(1, 0)
        assert left * right != right * left
    source = ring.free_module(("a", "z"))
    target = ring.free_module(("z", "a"))
    a, z = source.module_generator("a"), source.module_generator("z")
    p, q = target.module_generator("a"), target.module_generator("z")
    first = target.scalar_multiple(right, p) + target.scalar_multiple(left, q)
    second = target.scalar_multiple(left, p) + target.scalar_multiple(right, q)
    extension = Modules(ring).Mor(source, target)({"a": first, "z": second})

    assert extension(a) == first
    assert extension(z) == second
    assert extension(source.zero()) == target.zero()
    assert extension(-a) == -first
    assert extension(source.scalar_multiple(left, a) + source.scalar_multiple(right, z)) == (
        target.scalar_multiple(left, first) + target.scalar_multiple(right, second)
    )
